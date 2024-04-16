import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin
from typing import List
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]

    @classmethod
    def from_soup(cls, quote_soup: BeautifulSoup) -> "Quote":
        return cls(
            text=quote_soup.select_one(".text").text,
            author=quote_soup.select_one(".author").text,
            tags=[tag.get_text() for tag in quote_soup.select("a.tag")],
        )


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_single_page_quotes(page_soup: BeautifulSoup) -> List[Quote]:
    quotes = page_soup.select(".quote")
    return [Quote.from_soup(quote_soup) for quote_soup in quotes]


def get_home_products() -> List[Quote]:
    page = requests.get(BASE_URL).content
    page_soup = BeautifulSoup(page, "html.parser")

    all_products = get_single_page_quotes(page_soup)

    while page_soup.select_one("li.next"):
        next_page = requests.get(
            urljoin(BASE_URL, page_soup.select_one("li.next > a")["href"])
        ).content

        soup = BeautifulSoup(next_page, "html.parser")
        all_products.extend(get_single_page_quotes(soup))

        page_soup = soup

    return all_products


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in get_home_products()])


if __name__ == "__main__":
    main("quotes.csv")
