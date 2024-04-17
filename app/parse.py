import csv
from typing import Callable
from urllib.parse import urljoin

import httpx

from bs4 import BeautifulSoup
from dataclasses import dataclass, fields, astuple

from app.parse_authors import (
    find_author_url,
    parse_author,
    get_all_authors,
    AUTHOR_FIELDS
)


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    author_url = find_author_url(quote_soup)

    if author_url:
        parse_author(urljoin(BASE_URL, author_url + "/"))

    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[
            tag.text for tag in quote_soup.select(".tag")
        ],
    )


def has_next_page(page_soup: BeautifulSoup) -> bool:
    next_page = page_soup.select_one("ul.pager > li.next")

    if next_page:
        return True

    return False


def parse_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    page_quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in page_quotes]


def parse_paginated_page_quotes(
        page_soup: BeautifulSoup,
        client: httpx.Client
) -> list[Quote]:
    page_num = 2
    paginated_quotes = []

    while True:
        if not has_next_page(page_soup):
            break

        page = client.get(
            urljoin(BASE_URL, f"page/{page_num}/")
        ).content
        page_soup = BeautifulSoup(page, "html.parser")
        paginated_quotes.extend(parse_single_page_quotes(page_soup))

        page_num += 1

    return paginated_quotes


def parse_quotes(url: str) -> list[Quote]:
    with httpx.Client() as client:
        page = client.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = parse_single_page_quotes(soup)

        if has_next_page(soup):
            quotes.extend(parse_paginated_page_quotes(soup, client))

        return quotes


def write_to_csv(
        objects: list[Callable],
        output_csv_path: str,
        fields_list: list[str]
) -> None:
    with open(output_csv_path, "w+") as file:
        writer = csv.writer(file)
        writer.writerow(fields_list)
        writer.writerows([astuple(obj) for obj in objects])


def main(quotes_csv_path: str) -> None:
    quotes = parse_quotes(BASE_URL)
    authors = get_all_authors()

    write_to_csv(quotes, quotes_csv_path, QUOTE_FIELDS)
    write_to_csv(authors, "authors.csv", AUTHOR_FIELDS)


if __name__ == "__main__":
    main("quotes.csv")
