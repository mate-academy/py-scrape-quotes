import csv
from dataclasses import dataclass, fields, astuple
from typing import List

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


PRODUCT_FIELDS = [field.name for field in fields(Quote)]

BASE_URL = "https://quotes.toscrape.com/"


def parse_product(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_single_quote(soup: Tag) -> List[Quote]:
    quotes = soup.select(".quote")
    return [parse_product(quote) for quote in quotes]


def get_quotes() -> List[Quote]:
    page = 1
    all_quotes = []
    while True:
        text = requests.get(BASE_URL + f"page/{page}").content
        soup = BeautifulSoup(text, "html.parser")
        if not soup.select(".next"):
            all_quotes.extend(get_single_quote(soup))
            break
        page += 1
        all_quotes.extend(get_single_quote(soup))
    return all_quotes


def write_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_to_csv(get_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
