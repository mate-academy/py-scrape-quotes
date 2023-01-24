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


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[data.get_text() for data in quote_soup.select("a.tag")],
    )


def get_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> [Quote]:
    page = requests.get(BASE_URL).text
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_page_quotes(soup)

    while soup.select("li.next"):
        next_page = requests.get(
            urljoin(BASE_URL, soup.select_one("li.next > a")["href"])).text

        page_soup = BeautifulSoup(next_page, "html.parser")
        all_quotes.extend(get_page_quotes(page_soup))

        soup = page_soup

    return all_quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8") as file:
        wr = csv.writer(file)
        wr.writerow(field.name for field in fields(Quote))
        wr.writerows([astuple(quote) for quote in get_all_quotes()])


if __name__ == "__main__":
    main("quotes.csv")
