import csv
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quot_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quot_soup.select_one(".text").text,
        author=quot_soup.select_one(".author").text,
        tags=[tag.text for tag in quot_soup.select(".tag")]
    )


def single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:

    quotes = page_soup.select(".quote")
    return [parse_single_quote(quot_soup) for quot_soup in quotes]


def get_quotes() -> list[Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = []
    num_page = 1

    while soup.select_one(".next"):
        page = urljoin(BASE_URL, f"/page/{num_page}/")
        page = requests.get(page).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(single_page_quotes(soup))
        num_page += 1

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
