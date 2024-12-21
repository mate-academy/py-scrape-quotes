import csv
from typing import List
from urllib.parse import urljoin

import requests

from dataclasses import dataclass, astuple
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = ["text", "author", "tags"]

HOME_PAGE = "https://quotes.toscrape.com/"


def parse_single_quote(quote_element: Tag) -> Quote:
    return Quote(
        text=quote_element.select_one(".text").text,
        author=quote_element.select_one(".author").text,
        tags=[tag.text for tag in quote_element.select(".tag")],
    )


def get_next_page(page_soup: BeautifulSoup) -> str | None:
    next_url = page_soup.select_one(".pager .next a")
    if next_url:
        return next_url["href"]

    return None


def get_page_quotes(url: str = HOME_PAGE) -> List[Quote]:
    text = requests.get(url)

    page_soup = BeautifulSoup(text.text, "html.parser")

    quote_elements = page_soup.select(".quote")
    quotes = []
    if quote_elements:
        quotes = [
            parse_single_quote(quote_element)
            for quote_element in quote_elements
        ]

    next_url = get_next_page(page_soup)
    if next_url:
        url = urljoin(HOME_PAGE, next_url)
        next_quotes = get_page_quotes(url)
        quotes.extend(next_quotes)

    return quotes


def write_quotes_to_csv(quotes: List[Quote], filename: str) -> None:
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        for quote in quotes:
            writer.writerow(astuple(quote))


def main(output_csv_path: str) -> None:
    quotes = get_page_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
