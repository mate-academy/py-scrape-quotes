from dataclasses import dataclass
from typing import List
import csv
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page(url: str) -> BeautifulSoup:
    """Загрузить страницу и вернуть объект BeautifulSoup."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_quotes_from_soup(soup: BeautifulSoup) -> List[Quote]:
    """Достать все цитаты с одной страницы."""
    quotes: List[Quote] = []

    for quote_block in soup.select("div.quote"):
        text = quote_block.select_one("span.text").get_text(strip=True)
        author = quote_block.select_one("small.author").get_text(strip=True)

        tags = [
            tag.get_text(strip=True)
            for tag in quote_block.select("div.tags a.tag")
        ]

        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def iter_all_quotes() -> List[Quote]:
    """Итерироваться по всем страницам и собрать все цитаты."""
    all_quotes: List[Quote] = []
    current_url = BASE_URL

    while True:
        soup = fetch_page(current_url)
        page_quotes = parse_quotes_from_soup(soup)

        if not page_quotes:
            break

        all_quotes.extend(page_quotes)

        next_li = soup.select_one("li.next a")
        if not next_li:
            break

        next_href = next_li.get("href")
        current_url = urljoin(BASE_URL, next_href)

        time.sleep(0.3)

    return all_quotes


def write_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    """Записать цитаты в CSV-файл."""
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, ", ".join(quote.tags)])


def main(output_csv_path: str) -> None:
    quotes = iter_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
