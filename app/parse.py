import csv
from dataclasses import dataclass, fields, astuple
from typing import Iterable, Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_url_soup(url: str) -> BeautifulSoup:
    response = requests.get(url).content
    return BeautifulSoup(response, "html.parser")


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one("span.text").text,
        author=quote_soup.select_one("span > small.author").text,
        tags=[tag.text for tag in quote_soup.select(".tags > a.tag")],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def parse_quotes() -> list[Quote]:
    page_number = 1
    quotes = []
    while True:
        soup = get_url_soup(urljoin(TARGET_URL, f"page/{page_number}/"))
        quotes.extend(get_single_page_quotes(soup))
        if soup.select_one("li.next") is None:
            return quotes
        page_number += 1


def write_quotes_to_csv_file(
    output_csv_path: str, quotes: list[Quote], row: Iterable[Any]
) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(row)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = parse_quotes()
    write_quotes_to_csv_file(output_csv_path, quotes, QUOTE_FIELDS)


if __name__ == "__main__":
    main("quotes.csv")
