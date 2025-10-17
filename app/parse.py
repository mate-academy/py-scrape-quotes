import csv
from dataclasses import dataclass
from typing import Generator, List, Dict
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

URL = "https://quotes.toscrape.com/"

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


def fetch_page(page_url: str) -> bytes | None:
    print(f"Fetching page {page_url}")
    response = requests.get(page_url)

    if response.status_code == 200:
        return response.content


def page_generator() -> Generator[BeautifulSoup, None, None]:
    page_number = 0

    for _ in range(10):
        page_number += 1
        page_url = urljoin(URL, f"page/{page_number}/")

        content = fetch_page(page_url)
        if not content:
            break

        soup = BeautifulSoup(content, "html.parser")
        yield soup


def get_author(author_link: str) -> Author | None:
    author_link = urljoin(URL, author_link)
    print(f"Fetching page {author_link}")
    author_page = requests.get(author_link)
    if author_page.status_code != 200:
        return

    soup = BeautifulSoup(author_page.content, "html.parser")

    author_element = soup.select_one(".author-details")
    name = author_element.select_one("h3.author-title").text
    born_date = author_element.select_one("span.author-born-date").text
    born_location = author_element.select_one("span.author-born-location").text[3:]
    description = author_element.select_one(".author-description").text
    return Author(
        name=name,
        born_date=born_date,
        born_location=born_location,
        description=description,
    )

def parse_page(page: BeautifulSoup, quotes: list, authors: dict) -> None:

    for element in page.select(".quote"):
        quote_text = element.select_one("span.text").text
        quote_author = element.select_one("small.author").text
        author_link = element.select_one("a[href]")["href"]

        tags = []
        for tag in element.select("a.tag"):
            tags.append(tag.text)
        quotes.append(Quote(text=quote_text, author=quote_author, tags=tags))

        if quote_author not in authors:
            author = get_author(author_link)
            if author:
                authors[quote_author] = author


def get_quotes_and_authors() -> tuple[List[Quote], Dict[str, Author]]:
    quotes = []
    authors = {}

    for page in page_generator():
        parse_page(page, quotes, authors)

    return quotes, authors


def write_quotes_to_file(output_csv_path: str, quotes: List[Quote]):
    print("Writing quotes to file")
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for quote in quotes:
            writer.writerow({
                "text": quote.text,
                "author": quote.author,
                "tags": quote.tags,
            })

    print(f"Quotes saved to {output_csv_path}")


def write_authors_to_file(output_csv_path: str, authors: Dict[str, Author]):
    print("Writing author to file")
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["name", "born_date", "born_location", "description"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for author_name in sorted(authors.keys()):
            author = authors[author_name]
            writer.writerow({
                "name": author.name,
                "born_date": author.born_date,
                "born_location": author.born_location,
                "description": author.description,
            })


def main(output_csv_path: str, authors_csv_path: str = "authors.csv") -> None:
    quotes, authors = get_quotes_and_authors()
    write_quotes_to_file(output_csv_path, quotes)
    write_authors_to_file(authors_csv_path, authors)

if __name__ == "__main__":
    main("quotes.csv")
