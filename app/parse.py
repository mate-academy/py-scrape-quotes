import csv
from dataclasses import astuple, dataclass, fields
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    birth_date: str
    birth_location: str
    decription: str


BASE_URL = "https://quotes.toscrape.com"

QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


cached_author_links = set()


def parse_single_quote(quote_soup: Tag) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = [tag.text for tag in quote_soup.select(".tag")]

    quote = Quote(
        text=text,
        author=author,
        tags=tags,
    )

    author_link = quote_soup.select_one("span a").get("href")
    cached_author_links.add(f"{author_link}/")

    return quote


def get_single_quote_page(soup: Tag) -> list[Quote]:
    quotes_soup = soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes_soup]


def get_quotes_pages() -> list[Quote]:
    response = requests.get(BASE_URL)
    first_page_soup = BeautifulSoup(response.content, "html.parser")

    quotes = get_single_quote_page(first_page_soup)

    pager = first_page_soup.select_one(".next")
    current_page_num = 1

    while pager:
        current_page_num += 1
        addition_url = f"/page/{current_page_num}/"

        current_url = urljoin(BASE_URL, addition_url)
        response = requests.get(current_url)

        current_page_soup = BeautifulSoup(response.content, "html.parser")
        pager = current_page_soup.select_one(".next")

        quotes.extend(get_single_quote_page(current_page_soup))

    return quotes


def parse_single_author(author_soup: Tag) -> Author:
    name = author_soup.select_one(".author-title").text
    birth_date = author_soup.select_one(".author-born-date").text
    birth_location = author_soup.select_one(".author-born-location").text
    description = author_soup.select_one(".author-description").text.strip()

    author = Author(
        name=name,
        birth_date=birth_date,
        birth_location=birth_location,
        decription=description,
    )

    return author


def get_single_author_page(soup: Tag) -> list[Author]:
    authors_soup = soup.select(".author-details")
    return [parse_single_author(author_soup) for author_soup in authors_soup]


def get_authors_pages() -> list[Author]:
    response = requests.get(BASE_URL)

    authors = []

    for link in cached_author_links:
        current_url = urljoin(BASE_URL, link)
        response = requests.get(current_url)

        current_page_soup = BeautifulSoup(response.content, "html.parser")

        authors.extend(get_single_author_page(current_page_soup))

    return authors


def write_to_csv_file(
    path: str,
    objects: list[Any],
    fields: list[str] | None = None
) -> None:
    with open(path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)

        if fields:
            writer.writerow(fields)

        writer.writerows([astuple(object_) for object_ in objects])


def main(
    quotes_output_csv_path: str,
    author_output_csv_path: str | None = None
) -> None:
    quotes = get_quotes_pages()
    write_to_csv_file(quotes_output_csv_path, quotes, QUOTE_FIELDS)

    if author_output_csv_path:
        authors = get_authors_pages()
        write_to_csv_file(author_output_csv_path, authors, AUTHOR_FIELDS)


if __name__ == "__main__":
    main("quotes.csv", "authors.csv")
