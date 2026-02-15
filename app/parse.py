from __future__ import annotations

import csv
import time
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com"


def _get_soup(session: requests.Session, url: str) -> BeautifulSoup:
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def _parse_page_quotes(soup: BeautifulSoup) -> list[Quote]:
    quotes: list[Quote] = []

    for block in soup.select(".quote"):
        text_el = block.select_one(".text")
        author_el = block.select_one(".author")
        tag_els = block.select(".tags .tag")

        if not text_el or not author_el:
            continue

        quotes.append(
            Quote(
                text=text_el.get_text(strip=True),
                author=author_el.get_text(strip=True),
                tags=[t.get_text(strip=True) for t in tag_els],
            )
        )
    return quotes


def _get_next_page_url(soup: BeautifulSoup) -> str | None:
    next_link = soup.select_one("li.next > a")
    href = next_link.get("href") if next_link else None
    return f"{BASE_URL}{href}" if href else None


def main(output_csv_path: str) -> None:
    delay_sec = 0.2

    with requests.Session() as session, open(
            output_csv_path, "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.writer(f)

        writer.writerow(["text", "author", "tags"])

        url: str | None = BASE_URL
        while url:
            soup = _get_soup(session, url)
            for qe in _parse_page_quotes(soup):
                writer.writerow([qe.text, qe.author, repr(qe.tags)])

            url = _get_next_page_url(soup)
            if url:
                time.sleep(delay_sec)


if __name__ == "__main__":
    main("quotes.csv")
