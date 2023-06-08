import csv
import logging
import sys
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://quotes.toscrape.com/"
QUOTES_URL = urljoin(BASE_URL, "page/1/")
QUOTES_OUTPUT_CSV_PATH = "correct_quotes.csv"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]:  %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=quote_soup.select_one(".tags")
        .text.replace("Tags:", " ")
        .replace("\n", " ")
        .strip()
        .split(),
    )


def get_num_pages() -> int:
    count_pages = 1

    while True:
        page = requests.get(f"{BASE_URL}page/{count_pages}/").content
        soup = BeautifulSoup(page, "html.parser")
        pagination = soup.select(".next")

        if not pagination:
            break

        count_pages += 1

    return count_pages


def get_single_quote(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> [Quote]:
    logging.info("Start parsing quotes")
    page = requests.get(QUOTES_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    num_pages = get_num_pages()

    all_quotes = get_single_quote(first_page_soup)

    for page_num in range(2, num_pages + 1):
        logging.info(f"Start parsing page #{page_num}")
        page = requests.get(f"{BASE_URL}/page/{page_num}/").content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_quote(soup))

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()

    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
