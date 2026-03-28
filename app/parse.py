import requests
import csv
from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.parse_authors import write_authors_to_csv, get_all_authors

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    tags = quote.select_one(".keywords")["content"]
    tags = [tag for tag in tags.split(",")] if tags else []

    return Quote(
        author=quote.select_one(".author").text,
        text=quote.select_one(".text").text,
        tags=tags
    )


def get_quotes_per_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_paginated_pages() -> list[Quote]:
    response = requests.get(BASE_URL).content
    page_soup = BeautifulSoup(response, "html.parser")
    all_quotes = get_quotes_per_page(page_soup)
    pagination = page_soup.select_one("li.next a")
    while pagination is not None:
        next_tag = pagination["href"]
        new_url = urljoin(BASE_URL, next_tag)
        response = requests.get(new_url).content
        new_page_soup = BeautifulSoup(response, "html.parser")
        all_quotes.extend(get_quotes_per_page(new_page_soup))
        pagination = new_page_soup.select_one("li.next a")

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes_csv = output_csv_path
    authors_csv = f"authors_{output_csv_path}"

    write_quotes_to_csv(get_paginated_pages(), quotes_csv)
    write_authors_to_csv(get_all_authors(), authors_csv)


if __name__ == "__main__":
    main("quotes.csv")
