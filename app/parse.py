import csv
import logging
from dataclasses import dataclass
from logger_config import logging

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
OUTPUT_FILE = "quotes.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_quotes_from_page(soup: BeautifulSoup) -> [Quote]:
    quotes = soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_list_quotes() -> list[Quote]:
    quotes = []
    page = 1

    logging.info("Start parsing Quotes")

    while True:
        logging.info(f"Start parsing page #{page}")
        url = f"{BASE_URL}/page/{page}/"
        parsed_page = requests.get(url).content
        page_soup = BeautifulSoup(parsed_page, "html.parser")
        parsed_quotes = get_quotes_from_page(page_soup)

        if not parsed_quotes:
            break

        quotes.extend(parsed_quotes)
        page += 1

    return quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_list_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
