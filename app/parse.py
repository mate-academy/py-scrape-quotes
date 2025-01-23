import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def parse_qutes(soup: Tag) -> list[Quote]:
    quotes = [parse_single_quote(quote) for quote in soup.select(".quote")]
    while next := soup.select_one(".next > a"):
        text = requests.get(BASE_URL + next["href"]).content
        soup = BeautifulSoup(text, "html.parser")
        quotes.extend(
            [parse_single_quote(quote) for quote in soup.select(".quote")]
        )
    return quotes


def main(output_csv_path: str) -> None:
    text = requests.get(BASE_URL).content
    soup = BeautifulSoup(text, "html.parser")
    quotes = parse_qutes(soup)

    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
