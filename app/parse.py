import os
import csv
import urllib.parse
from dataclasses import dataclass
from functools import lru_cache

import requests
from bs4 import BeautifulSoup


QUOTES_CSV_PATH = "quotes.csv"
AUTHORS_CSV_PATH = "authors.csv"

QUOTES_BASE_URL = "https://quotes.toscrape.com/"
QUOTES_PAGE_URL = urllib.parse.urljoin(QUOTES_BASE_URL, "/page/{page_number}/")


@dataclass(frozen=True)
class Author:
    name: str
    born: str
    bio: str


@dataclass
class Quote:
    text: str
    author: Author
    tags: list[str]


def get_quotes_page(page_number: int) -> str:
    page_link = QUOTES_PAGE_URL.format(page_number=page_number)
    response = requests.get(page_link)
    response.raise_for_status()
    return response.text


@lru_cache
def get_author_about_page(author_about_url: str) -> str:
    author_page_url = urllib.parse.urljoin(QUOTES_BASE_URL, author_about_url)
    response = requests.get(author_page_url)
    response.raise_for_status()
    return response.text


@lru_cache
def parse_author_page(author_page: str) -> Author:
    soup = BeautifulSoup(author_page, "html.parser")
    name = soup.find("h3").text.strip().replace("-", " ")
    born = soup.find("span", class_="author-born-date").text.strip()
    bio = soup.find("div", class_="author-description").text.strip()

    return Author(name=name, born=born, bio=bio)


def parse_quotes_page(page_html: str) -> list[Quote]:
    soup = BeautifulSoup(page_html, "html.parser")
    quotes = []
    for quote_div in soup.find_all("div", class_="quote"):
        text = quote_div.find("span", class_="text").text.strip()
        author_about_url = quote_div.find("a", string="(about)")["href"]
        author = parse_author_page(get_author_about_page(author_about_url))
        tags = [
            tag.text.strip()
            for tag in quote_div.find_all("a", class_="tag")
        ]
        quotes.append(Quote(text=text, author=author, tags=tags))
    return quotes


def save_to_csv(
    quotes: list[Quote],
    quotes_csv_path: str,
    authors_csv_path: str,
) -> None:
    with open(quotes_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author.name, str(quote.tags)])

            save_author_to_csv(authors_csv_path, quote.author)


@lru_cache
def save_author_to_csv(authors_csv_path: str, author: Author) -> None:
    is_file_exists = os.path.isfile(authors_csv_path)
    with open(authors_csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not is_file_exists:
            writer.writerow(["name", "born", "bio"])
        writer.writerow([author.name, author.born, author.bio])


def main(
    quotes_csv_path: str = QUOTES_CSV_PATH,
    authors_csv_path: str = AUTHORS_CSV_PATH
) -> None:
    page_number = 1
    all_quotes: list[Quote] = []

    while True:
        page_html = get_quotes_page(page_number)
        quotes = parse_quotes_page(page_html)
        if not quotes:
            break
        all_quotes.extend(quotes)
        page_number += 1

    save_to_csv(all_quotes, quotes_csv_path, authors_csv_path)


if __name__ == "__main__":
    main(QUOTES_CSV_PATH, AUTHORS_CSV_PATH)
