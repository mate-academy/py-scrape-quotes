import csv
from typing import Generator
from urllib.parse import urljoin

import requests
from dataclasses import dataclass, fields
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


FIELDS = [field.name for field in fields(Quote)]

session = requests.Session()
session.headers.update(
    {"User-Agent": "Mozilla/5.0 (compatible; QuotesScraper/1.0)"}
)


def get_quotes() -> Generator[Quote, None, None]:
    count = 1
    while True:
        next_page = urljoin(BASE_URL, f"page/{count}/")
        try:
            response = session.get(next_page, timeout=5)
        except requests.RequestException:
            break

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, "html.parser")
        quotes = soup.select(".quote")
        if not quotes:
            break

        for quote in quotes:
            yield parse_quote(quote)
        count += 1


def parse_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def make_dict(quote: Quote) -> dict:
    return {
        "text": quote.text,
        "author": quote.author,
        "tags": ";".join(tag for tag in quote.tags)
    }


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for quote in get_quotes():
            writer.writerow(make_dict(quote))


if __name__ == "__main__":
    main("quotes.csv")
