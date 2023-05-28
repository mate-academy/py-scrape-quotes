import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

logging.basicConfig(
     level=logging.INFO,
     format="[%(levelname)8s]:   %(message)s",
     handlers=[
         logging.FileHandler("parser.log"),
         logging.StreamHandler(sys.stdout),
     ],
 )


BASE_URL = "https://quotes.toscrape.com/"
QUOTE_OUTPUT_CSV_PATH = "quotes.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def next_page_is_exist(soup: BeautifulSoup):
    return bool(soup.select_one(".next"))


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_quotes_from_single_page(soup: BeautifulSoup) -> [Quote]:
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> [Quote]:
    logging.info("Start parsing quotes")
    page = requests.get(BASE_URL).content
    page_num = 2

    soup = BeautifulSoup(page, "html.parser")
    quotes = get_quotes_from_single_page(soup)

    while next_page_is_exist(soup):
        logging.info(f"Page number {page_num}")
        page = requests.get(urljoin(BASE_URL, f"page/{page_num}")).content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(get_quotes_from_single_page(soup))
        page_num += 1

    return quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in get_quotes()])


if __name__ == "__main__":
    main(QUOTE_OUTPUT_CSV_PATH)
