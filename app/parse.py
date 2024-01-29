import csv
import logging
import sys
from dataclasses import dataclass
from typing import NoReturn

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)8s]: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_quote_list(quote_soup_list: list[BeautifulSoup]) -> [Quote]:
    return [Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=[tag.text for tag in soup.select(".tag")]
    ) for soup in quote_soup_list]


def get_quotes() -> [Quote]:
    quotes_list = []
    page_counter = 1

    logging.info("Start parsing")
    while True:
        url = f"{BASE_URL}/page/{page_counter}/"
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")

        quotes_list.extend(parse_quote_list(soup.select(".quote")))

        if not soup.select(".next"):
            break
        page_counter += 1
    return quotes_list


def write_quotes_to_csv(path: str, quotes: [Quote]) -> NoReturn:
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
