import csv
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, fields, astuple

BASE_URL = "https://quotes.toscrape.com"
HOME_URL = urljoin(BASE_URL, "/page/1")

QUOTES_OUTPUT_CSV_PATH = "quotes.csv"


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
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_next_page(page_soup: BeautifulSoup) -> str:
    next_page = page_soup.select_one(".pager > li.next > a")
    if next_page:
        return next_page["href"]


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:
    page = requests.get(HOME_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    next_page = get_next_page(first_page_soup)

    all_quotes = get_single_page_quotes(first_page_soup)
    while next_page is not None:
        page = requests.get(urljoin(BASE_URL, next_page)).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        next_page = get_next_page(soup)
    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: [Quote]) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    all_quotes = get_quotes()
    write_quotes_to_csv(output_csv_path, all_quotes)


if __name__ == "__main__":
    main(QUOTES_OUTPUT_CSV_PATH)
