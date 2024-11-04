import csv
import logging
import sys
from dataclasses import dataclass, astuple, fields

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)8s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("parser.log"),
    ]
)


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = (
        quote_soup.select_one(".tags").text
        .replace(" ", "").split("\n")
    )
    tags = [tag for tag in tags if tag and tag != "Tags:"]
    return Quote(text, author, tags)


def get_num_pages(page_soup: BeautifulSoup) -> int:
    page_soup.select_one()


def get_all_quotes() -> list[Quote]:
    logging.info("Getting quotes for 1 page")
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")
    num_pages = 10

    all_quotes = first_page_soup.select(".quote")
    for num in range(2, num_pages + 1):
        logging.info(f"Getting quotes for {num} page")
        page = requests.get(urljoin(BASE_URL, f"page/{num}/")).content
        page_soup = BeautifulSoup(page, "html.parser")
        all_quotes += page_soup.select(".quote")

    logging.info("Got all quotes")
    return [parse_single_quote(quote_soup) for quote_soup in all_quotes]


def write_quotes_to_csv(
        file_path: str,
        quotes: list[Quote]
) -> None:
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])

    print("File was wrote")


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
