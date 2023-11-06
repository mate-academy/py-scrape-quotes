import csv

import requests
from bs4 import BeautifulSoup

from dataclasses import dataclass, fields, astuple

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> [Quote]:
    quotes = []
    page_num = 1

    while True:
        page = requests.get(f"{BASE_URL}/page/{page_num}").content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes_from_page = get_single_page_quotes(soup)
        if not all_quotes_from_page:
            break
        quotes.extend(all_quotes_from_page)
        page_num += 1

    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
