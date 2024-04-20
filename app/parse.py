import csv
from dataclasses import dataclass, fields, astuple
from typing import List

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


PRODUCT_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: Tag) -> Quote:
    tags = quote_soup.select_one(".tags").text.split("\n")
    cleaned_list_tags = [
        tag.strip()
        for tag in tags
        if tag.strip() and tag.strip() != "Tags:"
    ]

    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=cleaned_list_tags
    )


def get_all_quote() -> [Quote]:
    all_quotes = []
    next_page_href = "/"
    while next_page_href:
        page = requests.get(BASE_URL + next_page_href).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = soup.select(".quote")
        all_quotes.extend(parse_single_quote(quote) for quote in quotes)
        a_tag_next = soup.select_one(".next > a")
        next_page_href = a_tag_next.attrs["href"] if a_tag_next else None
    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quote()
    with open(output_csv_path, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
