import csv
import sys
import requests
import logging

from bs4 import BeautifulSoup
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com/"


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ]
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_quotes() -> [Quote]:
    page_number = 0
    all_quotes = []
    while True:
        page_number += 1
        logging.info(f"Start parsing page {page_number}")
        url = urljoin(BASE_URL, f"page/{page_number}/")
        quotes = get_single_page(url)
        if not quotes:
            break
        all_quotes.extend(quotes)

    return all_quotes


def get_single_page(url: str) -> [Quote]:
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    quotes = soup.select(".quote")
    return [parse_single_quote(quotes_soup) for quotes_soup in quotes]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in get_quotes()])


if __name__ == "__main__":
    main("quotes.csv")
