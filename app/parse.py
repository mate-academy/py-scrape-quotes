import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup, Tag


URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_next_page(soup: BeautifulSoup) -> str:
    next_button = soup.select_one(".next > a")
    return next_button["href"] if next_button else None


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_single_page_quotes(soup: BeautifulSoup) -> list[Quote]:
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> list[Quote]:
    quotes = []
    text = requests.get(URL).content
    soup = BeautifulSoup(text, "html.parser")

    while True:
        quotes.extend(get_single_page_quotes(soup))
        next_page = get_next_page(soup)
        if not next_page:
            break
        text = requests.get(URL + next_page).content
        soup = BeautifulSoup(text, "html.parser")

    return quotes


def main(output_csv_path: str) -> None:
    with open(
            output_csv_path,
            "a",
            newline="",
            encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in get_quotes()])


if __name__ == "__main__":
    main("quotes.csv")
