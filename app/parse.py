import csv
import logging
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
    format="[%(levelname)8s]:   %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def parse_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quote_soups = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quote_soups]


def button_next_exist(soup: BeautifulSoup) -> bool:
    button_next = soup.select_one(".next")
    return True if button_next else False


def get_page_soup(url: str) -> BeautifulSoup:
    page = requests.get(url).content
    return BeautifulSoup(page, "html.parser")


def write_quotes_to_csv(output_csv_path: str, all_quotes: [Quote]) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in all_quotes])


def main(output_csv_path: str) -> None:
    page_soup = get_page_soup(BASE_URL)
    page_num = 1
    all_quotes = []

    logging.info(f"Start parsing quotes")
    while button_next_exist(page_soup):
        logging.info(f"Start parsing page number #{page_num}")
        all_quotes.extend(parse_single_page_quotes(page_soup))
        page_num += 1
        page_soup = get_page_soup(urljoin(BASE_URL, f"/page/{page_num}/"))

    logging.info(f"Start parsing page number #{page_num}")
    all_quotes.extend(parse_single_page_quotes(page_soup))

    write_quotes_to_csv(output_csv_path, all_quotes)


if __name__ == "__main__":
    main("quotes.csv")
