import csv
import logging
import sys

import requests

from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [fields.name for fields in fields(Quote)]


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


def parse_single_quote(soup: Tag) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=[tag.text for tag in soup.select("a.tag")]
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_pages_quotes() -> list[Quote]:
    logging.info("Start parsing quotes")
    text = requests.get(BASE_URL).content
    soup = BeautifulSoup(text, "html.parser")
    all_quotes = get_single_page_quotes(soup)
    page_no: int = 1

    while True:
        page_no += 1
        logging.info(f"Parsing page #{page_no}")
        text = requests.get(f"{BASE_URL}/page/{page_no}").content
        soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        if soup.select_one(".pager > .next") is None:
            break

    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(output_csv_path, get_all_pages_quotes())


if __name__ == "__main__":
    main("quotes.csv")
