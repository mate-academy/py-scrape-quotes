import csv

import requests
from dataclasses import dataclass, astuple, fields

from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return (Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    ))


def get_quotes() -> [Quote]:
    page = 1
    quotes = []

    while True:
        text = requests.get(f"{BASE_URL}/page/{page}").text
        soup = BeautifulSoup(text, "html.parser")
        for quote in soup.select(".quote"):
            quotes.append(parse_single_quote(quote))

        next_button = soup.select_one(".next")

        if not next_button:
            break

        page += 1

    return quotes


def write_quotes_to_csv(path: str, quotes: [Quote]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(output_csv_path, get_quotes())


if __name__ == "__main__":
    main("quotes.csv")
