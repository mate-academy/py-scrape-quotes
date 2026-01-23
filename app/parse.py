from __future__ import annotations

import csv
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE = "https://quotes.toscrape.com"


def _fetch_html(url: str) -> BeautifulSoup:
    """Завантажити сторінку та повернути парсер BeautifulSoup."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def _parse_quotes(soup: BeautifulSoup) -> Iterable[Quote]:
    """Дістати всі цитати зі сторінки."""
    for block in soup.select("div.quote"):
        text_el = block.select_one("span.text")
        author_el = block.select_one("small.author")
        tags_el = block.select("div.tags a.tag")

        if not text_el or not author_el:
            continue

        text = text_el.get_text(strip=True)
        author = author_el.get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag in tags_el] if tags_el else []
        yield Quote(text=text, author=author, tags=tags)


def _next_page_url(soup: BeautifulSoup) -> Optional[str]:
    """Повертає абсолютний URL наступної сторінки або None."""
    next_link = soup.select_one("li.next > a[href]")
    if not next_link:
        return None

    href = next_link.get("href", "")
    if href.startswith("/"):
        return f"{BASE}{href}"
    return f"{BASE}/{href.lstrip('./')}"


def main(output_csv_path: str) -> None:
    """Зібрати всі цитати з https://quotes.toscrape.com та записати у CSV."""
    url = BASE
    quotes: List[Quote] = []

    # (опційно) кеш авторів, якщо захочеш розширити до біографій:
    # author_cache: Dict[str, str] = {}

    while url:
        soup = _fetch_html(url)
        quotes.extend(_parse_quotes(soup))
        # Будь ввічливим до сайту
        time.sleep(0.2)
        url = _next_page_url(soup)

    # Запис у CSV
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote_item in quotes:
            writer.writerow(
                [quote_item.text, quote_item.author, "|".join(quote_item.tags)]
            )


if __name__ == "__main__":
    main("quotes.csv")
