import csv
from dataclasses import dataclass, fields, astuple
from typing import List

import requests
from bs4 import BeautifulSoup, Tag

URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


PRODUCT_FIELDS = [field.name for field in fields(Quote)]


def scrape_single_quote(quote: Tag) -> Quote:
    tags = quote.select_one(".tags").text.split("\n")
    clear_tags = [
        tag.strip() for tag in tags
        if tag.strip() and tag.strip() != "Tags:"
    ]
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=clear_tags,
    )


def scrape_all_quotes() -> list[Quote]:
    all_quotes = []
    next_page = "/"
    while next_page:
        page = requests.get(URL + next_page).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = soup.select(".quote")
        all_quotes.extend(
            scrape_single_quote(quote) for quote in quotes
        )
        a_tag = soup.select_one(".next > a")
        next_page = a_tag.attrs["href"] if a_tag else None
    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = scrape_all_quotes()
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows(
            astuple(quote) for quote in quotes
        )


if __name__ == "__main__":
    main("quotes.csv")
