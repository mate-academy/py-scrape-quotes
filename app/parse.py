import csv
from dataclasses import dataclass, fields
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_one_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def get_one_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [get_one_quote(quote) for quote in quotes]


def get_quotes() -> list[Quote]:
    num_page = 1
    all_quotes = []
    while True:
        page = requests.get(urljoin(BASE_URL, f"page/{num_page}/")).content
        soup = BeautifulSoup(page, "html.parser")
        result = get_one_page(soup)
        if not result:
            break
        all_quotes.extend(result)
        num_page += 1
    return all_quotes


def save_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(QUOTE_FIELDS)

        for quote in quotes:
            row = [quote.text, quote.author, quote.tags]
            writer.writerow(row)


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    save_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
