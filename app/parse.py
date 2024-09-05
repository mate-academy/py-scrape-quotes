import asyncio
import csv
import logging
import sys
from dataclasses import dataclass, astuple, fields
import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

import app.author_parse as author_parse

BASE_URL = "https://quotes.toscrape.com/"
PATH_TO_LOGS = os.path.join("..", "logs")


if not os.path.exists(PATH_TO_LOGS):
    os.makedirs(PATH_TO_LOGS)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(PATH_TO_LOGS, "parser.log")),
        logging.StreamHandler(sys.stdout),
    ],
)

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags > .tag")],
    )


def parse_page_with_quotes(quotes_soup: BeautifulSoup) -> [Quote]:
    for author in quotes_soup.select(".quote"):
        asyncio.run(author_parse.parse_single_author(author))

    return [
        parse_single_quote(quote) for quote in quotes_soup.select(".quote")
    ]


def save_quotes_to_csv(quotes: [Quote], quotes_file: str) -> None:
    with open(quotes_file, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    logging.info("Parsing page #1")
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    all_quotes = parse_page_with_quotes(first_page_soup)

    page_number = 2
    while True:
        page = requests.get(urljoin(BASE_URL, f"/page/{page_number}")).content
        soup = BeautifulSoup(page, "html.parser")

        if not soup.text.__contains__("No quotes found!"):
            logging.info(f"Parsing page #{page_number}")
            all_quotes.extend(parse_page_with_quotes(soup))
            page_number += 1
        else:
            break

    save_quotes_to_csv(all_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
