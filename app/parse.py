import csv
import logging
import sys
import time

import requests
from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup


BASE_URL = " https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s] - %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


def parse_single_quote(soup: BeautifulSoup) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=[tag.text for tag in soup.select(".tag")]
    )


def get_quotes() -> [Quote]:
    logging.info("Parsing quotes")
    page_number = 1
    quotes = []
    while True:
        logging.info(f"Parsing page {page_number}")
        page = requests.get(f"{BASE_URL}/page/{page_number}").content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(
            [
                parse_single_quote(quote_soup)
                for quote_soup in soup.select(".quote")
            ]
        )

        if not soup.select_one(".next"):
            break
        page_number += 1
        time.sleep(1)

    return quotes


def write_quotes_to_csv(quotes: [Quote], csv_path: str) -> None:
    with open(csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
