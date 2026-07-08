import logging
from dataclasses import dataclass, fields, astuple
import csv
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_COLUMNS = [field.name for field in fields(Quote)]


def write_to_csv(
        filename: str, columns: list[str], items: list[Any]
) -> None:
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        for item in items:
            writer.writerow(astuple(item))


def parse_quotes_page(page: BeautifulSoup) -> list[Quote]:
    raw_quotes = page.select("div.quote")
    quotes = [
        Quote(
            text=quote.select_one("span.text").text.strip(),
            author=quote.select_one("small.author").text.strip(),
            tags=[tag.text.strip() for tag in quote.select(".tag")],
        )
        for quote in raw_quotes
    ]
    return quotes


def parse_quotes_pages(base_url: str) -> list[Quote]:
    quotes = []
    page = 1
    sub_url = f"/page/{page}/"
    while True:
        url = urljoin(base_url, sub_url)
        logging.info(f"Parsing url: {url}")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "lxml")
        quotes.extend(parse_quotes_page(soup))
        sub_url = soup.select_one(".next a")
        if sub_url:
            sub_url = sub_url.get("href")
        else:
            break
    return quotes


def main(output_csv_path: str) -> None:
    quotes = parse_quotes_pages(BASE_URL)
    write_to_csv(output_csv_path, QUOTES_COLUMNS, quotes)


if __name__ == "__main__":
    main("quotes.csv")
