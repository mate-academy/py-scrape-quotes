import csv
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, astuple

BASE_URL = "https://quotes.toscrape.com/"
QUOTES_FIELDS = ["text", "author", "tags"]


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_next_page_soup(num: int) -> BeautifulSoup:
    pagination_url = f"page/{num}/"
    current_url = urljoin(BASE_URL, pagination_url)
    page = requests.get(current_url).content
    return BeautifulSoup(page, "html.parser")


def get_num_pages(page_soup: BeautifulSoup) -> int:
    num = 1

    while True:
        pagination = page_soup.select_one(".pager .next a")
        if pagination:
            num += 1
            page_soup = get_next_page_soup(num)
        else:
            break

    return num


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    num_pages = get_num_pages(first_page_soup)

    all_quotes = get_single_page_quotes(first_page_soup)

    for num in range(2, num_pages + 1):
        page_soup = get_next_page_soup(num)
        all_quotes.extend(get_single_page_quotes(page_soup))

    return all_quotes


def write_quotes_to_csv(quotes_output_csv_path: str, quotes: [Quote]) -> None:
    with open(
            quotes_output_csv_path,
            "w",
            newline="",
            encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        for quote in quotes:
            writer.writerow(astuple(quote))
