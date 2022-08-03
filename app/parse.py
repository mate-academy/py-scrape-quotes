import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout)
    ],
)


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=list(
            quote_soup.select_one(".keywords")["content"].replace(",", " ").split()
        ),
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def parse_all_quotes():
    logging.info(f"Start parsing...")
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")
    all_quotes = get_single_page_quotes(first_page_soup)
    page_number = 2

    while first_page_soup.select_one("li.next") is not None:
        logging.info(f"Parsing page #{page_number}")
        page = requests.get(f"{BASE_URL}/page/{page_number}/").content
        first_page_soup = BeautifulSoup(page, "html.parser")

        all_quotes.extend(get_single_page_quotes(first_page_soup))

        page_number += 1

    logging.info(f"Done!")

    return all_quotes


def write_quotes_to_csv(path: str, quotes: list[Quote]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = parse_all_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
