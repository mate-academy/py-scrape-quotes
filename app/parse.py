import csv
import logging
import sys
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout),
    ]
)


def get_num_pages(soup: BeautifulSoup) -> bool:
    element = soup.select_one(".next")
    return element is not None


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[
            tag.text.strip()
            for tag
            in quote_soup.select(".tags > a.tag")
        ],
    )


def get_single_page_products(soup: BeautifulSoup) -> list[Quote]:
    quotes = soup.find_all("div", {"class": "quote"})
    return [parse_single_quote(quote) for quote in quotes]


def parse_quotes() -> list[Quote]:
    all_quotes = []
    page_number = 1
    next_page = True
    while next_page:
        page = requests.get(BASE_URL + f"page/{page_number}/").content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_products(soup))
        if not get_num_pages(soup):
            next_page = False
        page_number += 1
    return all_quotes


def main(output_csv_path: str) -> None:
    all_quotes = parse_quotes()
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in all_quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
