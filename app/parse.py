import csv
import time
from dataclasses import dataclass, fields, astuple
from functools import lru_cache
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"
REQUEST_DELAY = 0.2
REQUEST_TIMEOUT = 10


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    born_date: str
    born_location: str
    description: str


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


def get_soup(url: str) -> BeautifulSoup:
    time.sleep(REQUEST_DELAY)  # be gentle to the website
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_single_quote(quote_soup: Tag) -> tuple[Quote, str]:
    quote = Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags .tag")],
    )
    author_url = urljoin(BASE_URL, quote_soup.select_one("a")["href"])
    return quote, author_url


def parse_page(page_soup: Tag) -> list[tuple[Quote, str]]:
    return [parse_single_quote(quote) for quote in page_soup.select(".quote")]


@lru_cache(maxsize=None)
def get_author(author_url: str) -> Author:
    # cached: every author page is loaded only once
    soup = get_soup(author_url)
    return Author(
        name=soup.select_one(".author-title").text.strip(),
        born_date=soup.select_one(".author-born-date").text.strip(),
        born_location=soup.select_one(".author-born-location").text.strip(),
        description=soup.select_one(".author-description").text.strip(),
    )


def get_all_quotes() -> tuple[list[Quote], list[Author]]:
    quotes = []
    authors = {}
    url = BASE_URL

    while url:
        page_soup = get_soup(url)
        for quote, author_url in parse_page(page_soup):
            quotes.append(quote)
            if author_url not in authors:
                authors[author_url] = get_author(author_url)

        next_link = page_soup.select_one("li.next > a")
        url = urljoin(BASE_URL, next_link["href"]) if next_link else None

    return quotes, list(authors.values())


def write_csv(path: str, header: list[str], rows: list[tuple]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def main(output_csv_path: str) -> None:
    quotes, authors = get_all_quotes()
    write_csv(
        output_csv_path,
        QUOTE_FIELDS,
        [astuple(quote) for quote in quotes],
    )
    write_csv(
        "authors.csv",
        AUTHOR_FIELDS,
        [astuple(author) for author in authors],
    )


if __name__ == "__main__":
    main("quotes.csv")
