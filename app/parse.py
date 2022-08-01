import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup


URL = "https://quotes.toscrape.com/"

AUTHORS_CSV_PATH = "authors.csv"

NUMBER_OF_PAGES = 10

AUTHORS_NAMES = []

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)8s]: %(message)s",
    handlers=[logging.FileHandler("parser.log"), logging.StreamHandler(sys.stdout)],
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    authors = []

    name: str
    born_date: str
    born_location: str
    description: str

    def __post_init__(self):
        self.authors.append(self)


QUOTE_FIELDS = [field.name for field in fields(Quote)]

AUTHOR_FIELDS = [field.name for field in fields(Author)]


def create_author(soup):
    return Author(
        name=soup.select_one(".author-title").text,
        born_date=soup.select_one(".author-born-date").text,
        born_location=soup.select_one(".author-born-location").text,
        description=soup.select_one(".author-description").text,
    )


def parse_author_page(url):
    page = requests.get(url, "html.parser").content
    author_soup = BeautifulSoup(page, features="html.parser")
    create_author(author_soup)


def create_quote(quote_soup):
    author = quote_soup.select_one(".author").text
    if author not in AUTHORS_NAMES:
        AUTHORS_NAMES.append(author)
        url = f'{URL}{quote_soup.select_one("a", string="(about)")["href"]}'
        parse_author_page(url)

    return Quote(
        text=quote_soup.select_one(".text").text,
        author=author,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def parse_single_page(quote_page_soup):
    quotes = quote_page_soup.select(".quote")
    return [create_quote(quote) for quote in quotes]


def get_all_quotes():
    quotes = []
    for i in range(NUMBER_OF_PAGES + 1):
        page = requests.get(f"{URL}page/{i}", "html.parser").content
        page_soup = BeautifulSoup(page, features="html.parser")
        quotes.extend(parse_single_page(page_soup))
    return quotes


def write_quotes_to_csv(path, quotes):
    with open(path, "w", encoding="UTF8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_authors_to_csv(path, authors):
    with open(path, "w", encoding="UTF8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows([astuple(quote) for quote in authors])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(output_csv_path, quotes)
    print("authors", Author.authors)
    write_authors_to_csv(AUTHORS_CSV_PATH, Author.authors)


if __name__ == "__main__":
    main("quotes.csv")
