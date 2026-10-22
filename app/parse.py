import csv
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from dataclasses import dataclass, fields, astuple

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quotes(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=list(tag.text for tag in quote.select(".tag"))
    )


def get_quotes_from_page(url: str) -> tuple[list[Quote], str | None]:
    text = requests.get(url).content
    soup = BeautifulSoup(text, "html.parser")
    quotes = soup.select(".quote")
    next_url = None
    if soup.select_one(".next") is not None:
        next_url = urljoin(BASE_URL, soup.select_one(".next a")["href"])
    return [[parse_single_quotes(quote) for quote in quotes], next_url]


def get_quotes() -> list[Quote]:
    all_quotes = []
    current_url = urljoin(BASE_URL, "page/1/")
    while current_url:
        quotes, next_url = get_quotes_from_page(current_url)
        all_quotes.extend(quotes)
        current_url = next_url
        time.sleep(1)
    return all_quotes


def write_products_to_csv(
        quotes: list[Quote],
        filename: str
) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    write_products_to_csv(get_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
