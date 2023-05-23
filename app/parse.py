import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]:   %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    title: str | None
    birth_date: str | None
    location: str | None
    description: str | None

    author_links = set()
    authors = []


QUOTES_FIELDS = [field.name for field in fields(Quote)]
AUTHORS_FIELDS = [field.name for field in fields(Author)]


def next_page_is_exists(page_soup: BeautifulSoup) -> bool:
    return bool(page_soup.select_one(".next"))


def parse_single_author(author_soup: BeautifulSoup) -> Author:
    try:
        title = author_soup.select_one(".author-title").text.split("\n")[0]
    except AttributeError:
        title = None
    try:
        birth_date = (
            author_soup.select_one(".author-born-date").text.split("\n")[0]
        )
    except AttributeError:
        birth_date = None
    try:
        location = author_soup.select_one(".author-born-location").text[3:]
    except AttributeError:
        location = None
    try:
        description = (
            author_soup.select_one(".author-description").text.strip("\n")[8:]
        )
    except AttributeError:
        description = None
    return Author(
        title=title,
        birth_date=birth_date,
        location=location,
        description=description,
    )


def get_single_author_soup(author_url: str) -> BeautifulSoup:
    page = requests.get(author_url).content
    return BeautifulSoup(page, "html.parser")


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    author_link = quote_soup.select_one("a")["href"]
    if author_link not in Author.author_links:
        Author.author_links.add(author_link)
        author_soup = get_single_author_soup(urljoin(BASE_URL, author_link))
        author = parse_single_author(author_soup)
        Author.authors.append(author)
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_quotes_from_single_page(quote_soup: BeautifulSoup) -> [Quote]:
    quotes = quote_soup.select(".quote")
    return [parse_single_quote(soup) for soup in quotes]


def get_all_quotes() -> list[Quote]:
    logging.info("Start parsing quotes")
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    all_quotes = get_quotes_from_single_page(soup)
    page_num = 2

    while next_page_is_exists(soup) is True:
        logging.info(f"Start parsing page number {page_num}")
        page = requests.get(urljoin(BASE_URL, f"page/{page_num}")).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_quotes_from_single_page(soup))
        page_num += 1

    return all_quotes


def main(output_csv_path: str) -> None:
    with open(
            output_csv_path, "w", newline="", encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in get_all_quotes()])
    with open(
            "authors.csv", "w", newline="", encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(AUTHORS_FIELDS)
        writer.writerows([astuple(author) for author in Author.authors])


if __name__ == "__main__":
    main("quotes.csv")
