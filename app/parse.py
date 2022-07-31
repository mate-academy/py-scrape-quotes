import csv
import os.path
import requests

from dataclasses import dataclass, astuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"

QUOTES_OUTPUT_PATH = "quotes.csv"
QUOTES_COLUMN_NAMES = ("text", "author", "tags")

AUTHORS_OUTPUT_PATH = "authors.csv"
AUTHORS_COLUMN_NAMES = ("Name", "Birth day", "Born location", "Description")


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


author_cache = set()


def parse_author(author_data):
    author_name = author_data.select_one(".author").text
    author_url = author_data.select_one("span a")["href"]

    if author_url not in author_cache:
        soup = get_soup(urljoin(BASE_URL, author_url))
        author = Author(
            name=author_name,
            born_date=soup.select_one(".author-born-date").text,
            born_location=soup.select_one(".author-born-location").text,
            description=soup.select_one(".author-description").text
        )

        write_author_to_file(author)
        author_cache.add(author_url)

    return author_name


def parse_single_quote(quote_data):
    author_name = parse_author(quote_data)

    return Quote(
        text=quote_data.select_one(".text").text,
        author=author_name,
        tags=[tag.text for tag in quote_data.select(".tag")])


def get_single_page_quotes(soup):
    quotes = soup.select(".quote")
    all_quotes = [
        parse_single_quote(quote)
        for quote in quotes
    ]
    return all_quotes


def write_elements_to_file(elements, path):
    with open(path, mode="a", encoding="UTF8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows([astuple(element) for element in elements])


def write_quotes_to_file(quotes, output_csv_path):
    if not os.path.exists(output_csv_path):
        with open(
                output_csv_path,
                mode="w",
                encoding="UTF8",
                newline=""
        ) as file:
            writer = csv.writer(file)
            writer.writerow(QUOTES_COLUMN_NAMES)
    write_elements_to_file(elements=quotes, path=output_csv_path)


def write_author_to_file(author):
    if not os.path.exists(AUTHORS_OUTPUT_PATH):
        with open(
                AUTHORS_OUTPUT_PATH,
                mode="w",
                encoding="UTF8",
                newline=""
        ) as file:
            writer = csv.writer(file)
            writer.writerow(AUTHORS_COLUMN_NAMES)
    write_elements_to_file(elements=(author,), path=AUTHORS_OUTPUT_PATH)


def get_soup(url):
    page = requests.get(url).content
    return BeautifulSoup(page, "html.parser")


def main(output_csv_path: str) -> None:
    target_url = BASE_URL
    while True:
        soup = get_soup(target_url)
        quotes = get_single_page_quotes(soup)
        write_quotes_to_file(quotes, output_csv_path)
        next_page = soup.select_one(".next")
        if not next_page:
            break
        next_page_url = next_page.select_one("a")["href"]
        target_url = urljoin(BASE_URL, next_page_url)


if __name__ == "__main__":
    main(QUOTES_OUTPUT_PATH)
