import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import Tag, BeautifulSoup

MAIN_URL = "https://quotes.toscrape.com/"


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
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text.strip(),
        author=quote.select_one(".author").text.strip(),
        tags=[tag.text.strip() for tag in quote.select(".tag")]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quote_pages() -> list[Quote]:
    logging.info("Start parsing quotes")
    all_quotes = []

    current_url = MAIN_URL
    while current_url:
        logging.info(f"Fetching URL: {current_url}")
        response = requests.get(current_url)
        soup = BeautifulSoup(response.content, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))

        next_button = soup.select_one(".next > a")
        if next_button:
            current_url = urljoin(MAIN_URL, next_button["href"])
        else:
            current_url = None
            logging.info("Pagination finished")

    return all_quotes


def write_quotes_to_csv(file_name: str, quotes: list[Quote]) -> None:
    with open(file_name, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(output_csv_path, get_quote_pages())


if __name__ == "__main__":
    main("quotes.csv")
