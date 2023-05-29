import csv
from dataclasses import dataclass, fields
from urllib.parse import urljoin

import requests as requests
from bs4 import BeautifulSoup

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
        tags=[i.text for i in quote_soup.select(".tag")]
    )


def parse_page(page_soup: BeautifulSoup) -> list[Quote]:
    return [parse_single_quote(quote_soap) for quote_soap in page_soup]


def get_all_quotes() -> list[Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    num_page = 2
    quotes = parse_page(soup.select(".quote"))

    while soup.select_one(".next"):
        page = requests.get(urljoin(BASE_URL, f"page/{num_page}/")).content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(parse_page(soup.select(".quote")))
        num_page += 1

    return quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        for quote in get_all_quotes():
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
