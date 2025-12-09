from __future__ import annotations
import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    tags = quote.select_one(".tags")
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in tags.select(".tag")]
    )


def parse_single_page(url: str) -> list[Quote]:
    text = requests.get(url).content
    soup = BeautifulSoup(text, "html.parser")
    quotes = [parse_single_quote(quote_tag) for quote_tag in soup.select(".quote")]
    return quotes


def parse_all_pages() -> list[Quote]:
    results: list[Quote] = []
    url: str | None = BASE_URL

    while url:
        text = requests.get(url).content
        soup = BeautifulSoup(text, "html.parser")

        quotes = [parse_single_quote(quote_tag) for quote_tag in soup.select(".quote")]
        results.extend(quotes)

        next_page_tag = soup.select_one(".next a")
        url = urljoin(BASE_URL, next_page_tag["href"]) if next_page_tag else None

    return results


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        quotes = parse_all_pages()
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
