import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple

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
    level=logging.DEBUG,
    format="[%(levelname)8s]: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> [Quote]:
    logging.info("Start parsing")
    all_quotes = []
    page_num = 1

    while True:
        page = requests.get(f"{BASE_URL}/page/{page_num}").content
        page_soup = BeautifulSoup(page, "html.parser")

        all_quotes.extend(get_single_page_quotes(page_soup))

        page_num += 1

        if not page_soup.select_one(".next"):
            break

    return all_quotes


def write_quotes_to_csv(csv_path: str, quotes: [Quote]) -> None:
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
