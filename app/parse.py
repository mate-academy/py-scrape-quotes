import csv
import logging
import os
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("parser.log")),
        logging.StreamHandler(sys.stdout)
    ]
)


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def next_page_exist(page_soup: BeautifulSoup) -> int:
    return bool(page_soup.select_one(".next"))


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:
    logging.info("Start parsing quotes")
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(soup)
    num_page = 2

    while next_page_exist(soup):
        logging.info(f"Start parsing page #{num_page}")
        page = requests.get(urljoin(BASE_URL, f"page/{num_page}")).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        num_page += 1

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], file_path: str) -> None:
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes=quotes, file_path=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
