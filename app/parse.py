import csv
from dataclasses import dataclass, astuple
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

PARSE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_page(page_soup: BeautifulSoup) -> Optional[urljoin]:
    pagination = page_soup.select_one(".pager .next")
    if pagination:
        return urljoin(PARSE_URL, pagination.select_one("a")["href"])


def get_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return list(map(parse_single_quote, quotes))


def parse_all_pages() -> list[Quote]:
    quotes_list = []
    page_url = PARSE_URL

    while page_url:
        page = requests.get(page_url).content
        soup = BeautifulSoup(page, "html.parser")

        quotes = get_quotes(soup)
        quotes_list.extend(quotes)

        page_url = get_page(soup)
    return quotes_list


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w") as quotes:
        fields = ["text", "author", "tags"]
        writer = csv.writer(quotes)
        writer.writerow(fields)

        quotes_list = parse_all_pages()

        for quote in quotes_list:
            writer.writerow(astuple(quote))


if __name__ == "__main__":
    main("quotes.csv")
