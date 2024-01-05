import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    date: str
    location: str
    description: str


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


AUTHOR_LINKS = []


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)8s]: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


def parse_single_author(author_soup: BeautifulSoup) -> Author:
    return Author(
        name=author_soup.select_one(".author-title").text,
        date=author_soup.select_one(".author-born-date").text,
        location=author_soup.select_one(".author-born-location").text,
        description=author_soup.select_one(".author-description").text
    )


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    author_link = BASE_URL + quote_soup.select_one("a")["href"]
    if author_link not in AUTHOR_LINKS:
        AUTHOR_LINKS.append(author_link)

    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> [Quote]:
    logging.info("Start parsing quotes")
    all_quotes = []
    page_num = 1

    while True:
        page = requests.get(f"{BASE_URL}/page/{page_num}").content
        page_soup = BeautifulSoup(page, "html.parser")

        all_quotes.extend(get_single_page_quotes(page_soup))

        page_num += 1

        if not page_soup.select_one(".next"):
            break

    return all_quotes


def get_authors() -> [Author]:
    logging.info("Start parsing authors")
    all_authors = []

    for author_link in AUTHOR_LINKS:
        page = requests.get(author_link).content
        page_soup = BeautifulSoup(page, "html.parser")

        author = parse_single_author(page_soup)
        all_authors.append(author)

    return all_authors


def write_quotes_to_csv(csv_path: str, quotes: [Quote]) -> None:
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_authors_to_csv(csv_path: str, authors: [Author]) -> None:
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows(astuple(author) for author in authors)


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    authors = get_authors()
    write_quotes_to_csv(output_csv_path, quotes)
    write_authors_to_csv("authors.csv", authors)


if __name__ == "__main__":
    main("quotes.csv")
