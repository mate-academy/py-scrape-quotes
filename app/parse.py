from __future__ import annotations

import csv
from dataclasses import dataclass

from bs4 import BeautifulSoup
import requests


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_next_page(page_number: int) -> BeautifulSoup | None:
    next_page_url = f"{BASE_URL}page/{page_number}/"
    page = requests.get(next_page_url)

    return BeautifulSoup(page.content, "html.parser")


def parse_page_quotes() -> list[Quote]:
    page = requests.get(BASE_URL).content
    page_soup = BeautifulSoup(page, "html.parser")
    quotes = []
    page_count = 1

    while page_soup:
        page_quotes = page_soup.select("div.quote")
        for quote in page_quotes:
            quotes.append(
                Quote(
                    text=quote.select_one(".text").text,
                    author=quote.select_one(".author").text,
                    tags=[tag.text for tag in quote.select(".tag")]
                )
            )

        next_page_exist = page_soup.select_one("nav > ul.pager > li.next")

        if not next_page_exist:
            return quotes

        page_count += 1
        page_soup = get_next_page(page_number=page_count)


def write_quote_to_csv(file_path: str, quotes: list[Quote]) -> None:
    with open(file_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        header = ["text", "author", "tags"]
        writer.writerow(header)

        for quote in quotes:
            writer.writerow([getattr(quote, attr) for attr in header])


def main(output_csv_path: str) -> None:
    quotes = parse_page_quotes()

    write_quote_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
