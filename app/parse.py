import requests

from dataclasses import dataclass, astuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.writer import FileWriter

BASE_URL = "https://quotes.toscrape.com/"

QUOTES_OUTPUT_PATH = "quotes.csv"
QUOTES_COLUMN_NAMES = ("text", "author", "tags")

AUTHORS_OUTPUT_PATH = "authors.csv"
AUTHORS_COLUMN_NAMES = ("Name", "Birthday", "Born location", "Description")


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


def create_author(soup):
    return Author(
        name=soup.select_one(".author-title").text,
        born_date=soup.select_one(".author-born-date").text,
        born_location=soup.select_one(".author-born-location").text,
        description=soup.select_one(".author-description").text
    )


def parse_author(author_data):
    author_name = author_data.select_one(".author").text
    author_url = author_data.select_one("span a")["href"]
    author_writer = FileWriter(AUTHORS_OUTPUT_PATH, AUTHORS_COLUMN_NAMES)

    if author_url not in author_cache:
        soup = get_soup(urljoin(BASE_URL, author_url))
        author = create_author(soup)
        author_writer.write_elements(author)
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


def get_soup(url):
    page = requests.get(url).content
    return BeautifulSoup(page, "html.parser")


def main(output_csv_path: str) -> None:
    target_url = BASE_URL
    quotes_writer = FileWriter(output_csv_path, QUOTES_COLUMN_NAMES)
    while True:
        soup = get_soup(target_url)
        quotes = get_single_page_quotes(soup)
        quotes_writer.write_elements(quotes)
        next_page = soup.select_one(".next")
        if not next_page:
            break
        next_page_url = next_page.select_one("a")["href"]
        target_url = urljoin(BASE_URL, next_page_url)


if __name__ == "__main__":
    main(QUOTES_OUTPUT_PATH)
