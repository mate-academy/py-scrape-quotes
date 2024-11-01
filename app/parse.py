import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"

QUOTES_OUTPUT_CSV_PATH = "quotes.csv"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_single_quote(quote_html: Tag) -> Quote:
    return Quote(
        text=quote_html.select_one(".text").text,
        author=quote_html.select_one(".author").text,
        tags=[tag.text for tag in quote_html.select(".tag")]
    )


def get_single_page_quotes(page: str) -> list[Quote]:
    logging.info("Parsing quotes for a page")
    soup = BeautifulSoup(page, "html.parser")
    quotes_html = soup.select(".quote")
    quotes = [get_single_quote(quote) for quote in quotes_html]
    return quotes


def get_next_page_url(page: str) -> str:
    soup = BeautifulSoup(page, "html.parser")
    next_html = soup.select_one(".next > a")
    if next_html:
        return next_html["href"]


def get_quotes() -> list[Quote]:
    logging.info("Start parsing quotes")

    page = requests.get(BASE_URL).content
    quotes = get_single_page_quotes(page)

    next_page_url = get_next_page_url(page)
    while next_page_url is not None:
        new_url = urljoin(BASE_URL, next_page_url)
        page = requests.get(new_url).content
        quotes.extend(get_single_page_quotes(page))
        next_page_url = get_next_page_url(page)
    return quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    logging.info("Writing in a file")
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main(QUOTES_OUTPUT_CSV_PATH)
