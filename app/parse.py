import csv
from dataclasses import dataclass, astuple, fields
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"
PAGE_URL = urljoin(BASE_URL, "page/1/")


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
    pagination = page_soup.select_one(".pager")

    if pagination is None or not pagination.select(".next > a"):
        return None

    next_page = pagination.select_one(".next > a")["href"]
    next_page_url = urljoin(BASE_URL, next_page)
    return next_page_url


def get_quote_name() -> List[Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = []

    while True:
        quote = soup.select(".quote")
        all_quotes.extend(
            [parse_single_quote(quote_soup) for quote_soup in quote]
        )

        next_page_url = get_next_page(soup)
        if next_page_url:
            page = requests.get(next_page_url).content
            soup = BeautifulSoup(page, "html.parser")
        else:
            break

    return all_quotes


def write_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)

        quote_tuples = [astuple(quote) for quote in quotes]
        writer.writerows(quote_tuples)


def main(output_csv_path: str) -> None:
    quotes = get_quote_name()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
