from dataclasses import dataclass, fields, astuple

import csv
from typing import List

import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin


HOME_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELD = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=list(quote.select_one(".keywords")["content"].split(",")),
    )


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    current_url = HOME_URL

    with requests.Session() as session:
        while current_url:

            text = session.get(current_url).content

            soup = BeautifulSoup(text, "html.parser")
            quotes = soup.select(".quote")
            for quote in quotes:
                all_quotes.append(parse_single_quote(quote))

            next_button = soup.select_one(".next a")

            if next_button:
                current_url = urljoin(HOME_URL, next_button["href"])
            else:
                current_url = None

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELD)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
