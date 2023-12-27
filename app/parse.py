import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from typing import List

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags > .tag")],
    )


def get_single_page_quotes(soup: BeautifulSoup) -> List[Quote]:
    quotes = soup.select(".quote")

    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> List[Quote]:
    logging.info(f"Getting quotes from {BASE_URL}")
    response = requests.get(BASE_URL)

    first_page_soup = BeautifulSoup(response.text, "html.parser")

    page_number = 2

    all_quotes = get_single_page_quotes(first_page_soup)

    while True:
        logging.info(f"Getting quotes from {BASE_URL}page/{page_number}")

        page = requests.get(f"{BASE_URL}page/{page_number}")
        page_soup = BeautifulSoup(page.content, "html.parser")

        quotes = get_single_page_quotes(page_soup)
        all_quotes.extend(quotes)

        page_number += 1

        if page_soup.select_one(".next") is None:
            break

    return all_quotes


def write_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])
    logging.info(f"Products saved to {output_csv_path}")


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
