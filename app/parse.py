import csv
from dataclasses import dataclass
from typing import Any, Generator

import requests
from urllib.parse import urljoin

from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_pages() -> Generator[BeautifulSoup, Any, None]:
    page_number = 0
    while True:
        page_number += 1
        page_url = urljoin(BASE_URL, f"page/{page_number}/")
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, "html.parser")

        if not soup.select(".quote"):
            break

        yield soup


def parse_page(soup: BeautifulSoup) -> list[Quote]:
    quotes = soup.select(".quote")
    return [Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    ) for quote in quotes]


def parse_pages() -> list[Quote]:
    quotes = []
    for page_url in get_pages():
        quotes.extend(parse_page(page_url))
    return quotes


def main(output_csv_path: str) -> None:
    quotes = parse_pages()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([
                quote.text, quote.author, quote.tags
            ])


if __name__ == "__main__":
    main("quotes.csv")
