import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from typing import Tuple, List
from urllib.parse import urljoin

import requests
from bs4 import Tag, BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


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

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ]
)


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def parse_single_author(author: Tag) -> Author:
    return Author(
        name=author.select_one(".author-title").text,
        born_date=author.select_one(".author-born-date").text,
        born_location=author.select_one(".author-born-location")
        .text.lstrip("in "),
        description=author.select_one(".author-description").text.strip()
    )


def fetch_page(url: str) -> BeautifulSoup:
    response = requests.get(url)
    return BeautifulSoup(response.content, "html.parser")


def get_single_page_quotes(page_soup: Tag) -> List[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_author_urls(page_soup: Tag) -> List[str]:
    authors = page_soup.select("a[href^='/author/']")
    return [author["href"] for author in authors]


def get_single_author(page_soup: Tag) -> Author:
    author = page_soup.select_one(".author-details")
    return parse_single_author(author)


def write_items_to_csv(
    csv_path: str,
    items: List[Author | Quote],
    fields: List[str]
) -> None:
    with open(csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerows([astuple(item) for item in items])


def scrape_quotes_and_authors() -> Tuple[List[Quote], List[Author]]:
    logging.info("Start parsing quotes")

    soup = fetch_page(BASE_URL)
    all_quotes = get_single_page_quotes(soup)
    all_authors_urls = set(get_author_urls(soup))

    page_num = 2
    while soup.select_one(".next"):
        logging.info(f"Start parsing page {page_num}")
        next_page_url = urljoin(BASE_URL, f"page/{page_num}")
        soup = fetch_page(next_page_url)
        all_quotes.extend(get_single_page_quotes(soup))
        all_authors_urls.update(get_author_urls(soup))
        page_num += 1

    authors = []
    for author_url in all_authors_urls:
        logging.info("Start parsing author", author_url.lstrip("/author/"))

        next_page_url = urljoin(BASE_URL, author_url)
        soup = fetch_page(next_page_url)

        authors.append(get_single_author(soup))

    return all_quotes, authors


def main(quotes_csv_path: str, authors_csv_path: str = "authors.csv") -> None:
    quotes, authors = scrape_quotes_and_authors()

    write_items_to_csv(quotes_csv_path, quotes, QUOTE_FIELDS)
    write_items_to_csv(authors_csv_path, authors, AUTHOR_FIELDS)

    logging.info(f"Scraped {len(quotes)} quotes and {len(authors)} authors")


if __name__ == "__main__":
    main("quotes.csv")
