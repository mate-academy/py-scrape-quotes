import csv
import logging
import sys
import time
import random
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin


import requests
from bs4 import BeautifulSoup

HOME_URL = "https://quotes.toscrape.com/"

PAGE_URL = urljoin(HOME_URL, "page/")

AUTHOR_URL = urljoin(HOME_URL, "author/")


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


CSV_FIELDS_QUOTE = [field.name for field in fields(Quote)]


@dataclass
class Author:
    name: str
    born_date: str
    born_place: str
    description: str


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
        tags=[tag.text for tag in quote_soup.select("a.tag")],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(page_soup) for page_soup in quotes]


def get_quotes() -> [Quote]:
    logging.info("Start of quotes parsing")

    all_quotes = []

    page_num = 1
    current_page_url = urljoin(PAGE_URL, str(page_num))
    logging.info(current_page_url)
    first_page = requests.get(current_page_url).content
    first_page_soup = BeautifulSoup(first_page, "html.parser")
    present_next = first_page_soup.select_one(".next").text

    while present_next:
        logging.info(
            f"Requesting page {current_page_url} : status: {requests.get(current_page_url).status_code}"
        )
        time.sleep(random.randint(1, 10))

        page = requests.get(current_page_url).content
        page_soup = BeautifulSoup(page, "html.parser")

        all_quotes.extend(get_single_page_quotes(page_soup))
        present_next = page_soup.select_one(".next")

        page_num += 1
        current_page_url = urljoin(PAGE_URL, str(page_num))

    return all_quotes


def output_as_csv(path, quotes: [Quote]) -> None:
    with open(
        path,
        "w",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(CSV_FIELDS_QUOTE)
        writer.writerows([astuple(quote) for quote in quotes])

    logging.info(f"Saved {len(quotes)} quotes.")


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    output_as_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
