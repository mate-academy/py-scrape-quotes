import csv

from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"

AUTHORS_CSV_PATH = "authors.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    bio: str


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


def get_single_quote(quote_soup: Tag) -> (Quote, str):
    return (
        Quote(
            text=quote_soup.select_one(".text").text,
            author=quote_soup.select_one(".author").text,
            tags=[tag.text for tag in quote_soup.select(".tag")]
        ),
        urljoin(BASE_URL, quote_soup.select_one("a")["href"])
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [(Quote, str)]:
    quotes = page_soup.select(".quote")

    return [get_single_quote(quote_soup) for quote_soup in quotes]


def get_author_bio(
        author_url: str,
        authors_cache: dict[str, Author]
) -> Author:
    if author_url in authors_cache:
        return authors_cache[author_url]

    page = requests.get(author_url).content
    soup = BeautifulSoup(page, "html.parser")

    date = soup.select_one(".author-born-date").text
    location = soup.select_one(".author-born-location").text
    description = soup.select_one(".author-description").text
    author_bio = f"Born: {date} {location}. {description}"

    author = Author(
        name=soup.select_one(".author-title").text,
        bio=author_bio
    )

    authors_cache[author_url] = author

    return author


def get_all_quotes_and_authors() -> ([Quote], [Author]):
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    is_next = bool(first_page_soup.select_one(".next"))
    page_number = 1

    all_quotes = []
    authors_cache = {}

    quotes_and_authors = get_single_page_quotes(first_page_soup)
    all_quotes.extend(quote for quote, _ in quotes_and_authors)
    for _, url in quotes_and_authors:
        get_author_bio(url, authors_cache)

    while is_next:
        page_number += 1
        page = requests.get(urljoin(BASE_URL, f"page/{page_number}/")).content
        soup = BeautifulSoup(page, "html.parser")

        quotes_and_authors = get_single_page_quotes(soup)
        all_quotes.extend(quote for quote, _ in quotes_and_authors)
        for _, url in quotes_and_authors:
            get_author_bio(url, authors_cache)

        is_next = bool(soup.select_one(".next"))

    return all_quotes, list(authors_cache.values())


def write_to_csv(csv_file: str, rows: list, fields: list) -> None:
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(fields)
        writer.writerows([astuple(row) for row in rows])


def main(quotes_csv_path: str) -> None:
    quotes, authors = get_all_quotes_and_authors()
    write_to_csv(quotes_csv_path, quotes, QUOTE_FIELDS)
    write_to_csv(AUTHORS_CSV_PATH, authors, AUTHOR_FIELDS)


if __name__ == "__main__":
    main("quotes.csv")
