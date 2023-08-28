import csv
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quot_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quot_soup.select_one(".text").text,
        author=quot_soup.select_one(".author").text,
        tags=[tag.text for tag in quot_soup.select(".tag")]
    )


def get_quotes_from_single_page(url: str) -> list[Quote]:
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")

    quotes = soup.select(".quote")
    return [parse_single_quote(quot_soup) for quot_soup in quotes]


def has_next_page(url: str) -> bool:
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")

    next_page = soup.select_one(".next")

    if next_page:
        return True
    return False


def main(output_csv_path: str) -> None:
    quotes = []
    url = BASE_URL
    i = 1
    while has_next_page(url):
        url = urljoin(BASE_URL, f"/page/{i}/")
        quotes.extend(get_quotes_from_single_page(url))
        i += 1
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
