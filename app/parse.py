import csv
import time
from dataclasses import dataclass
from typing import Generator, List, Dict
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

URL = "https://quotes.toscrape.com/"
REQUEST_DELAY = 0.5
TIMEOUT = 10


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


session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
})


def fetch_page(page_url: str) -> bytes | None:
    print(f"Fetching page: {page_url}")
    try:
        response = session.get(page_url, timeout=TIMEOUT)
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return response.content
    except requests.RequestException as err:
        print(f"Failed to fetch {page_url}: {err}")
        return None


def page_generator() -> Generator[BeautifulSoup, None, None]:
    page_url = URL

    while True:
        content = fetch_page(page_url)
        if not content:
            break

        soup = BeautifulSoup(content, "html.parser")
        yield soup

        next_li = soup.select_one("li.next")
        if not next_li:
            break

        next_link = next_li.select_one("a")["href"]
        page_url = urljoin(URL, next_link)


def get_author(author_link: str) -> Author | None:
    author_link = urljoin(URL, author_link)
    print(f"Fetching author page: {author_link}")

    try:
        response = session.get(author_link, timeout=TIMEOUT)
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)
    except requests.RequestException as e:
        print(f"Failed to fetch author {author_link}: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    author_element = soup.select_one(".author-details")
    if not author_element:
        print(f"No author details found at {author_link}")
        return None

    name = author_element.select_one(
        "h3.author-title"
    ).get_text(strip=True)
    born_date = author_element.select_one(
        "span.author-born-date"
    ).get_text(strip=True)
    born_location = author_element.select_one(
        "span.author-born-location"
    ).get_text(strip=True)[3:]
    description = author_element.select_one(
        ".author-description"
    ).get_text(strip=True)

    return Author(name, born_date, born_location, description)


def parse_page(page: BeautifulSoup, quotes: list, authors: dict) -> None:
    for element in page.select(".quote"):
        quote_text = element.select_one("span.text").text
        quote_author = element.select_one("small.author").text
        author_link = element.select_one("a[href]")["href"]
        tags = [tag.text for tag in element.select("a.tag")]

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


def write_quotes_to_file(output_csv_path: str, quotes: List[Quote]) -> None:
    print(f"Writing quotes to file '{output_csv_path}'")
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


def write_authors_to_file(
        output_csv_path: str,
        authors: Dict[str, Author]
) -> None:
    print(f"Writing authors to file '{output_csv_path}'")
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

    print(f"Authors saved to {output_csv_path}")


def main(output_csv_path: str) -> None:
    quotes, authors = get_quotes_and_authors()
    write_quotes_to_file(output_csv_path, quotes)
    authors_csv_path = output_csv_path.replace(".csv", "_authors.csv")
    write_authors_to_file(authors_csv_path, authors)


if __name__ == "__main__":
    main("quotes.csv")
