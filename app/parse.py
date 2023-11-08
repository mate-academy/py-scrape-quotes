import sys
from csv import writer
from datetime import datetime
from dataclasses import astuple, fields
from urllib.parse import urljoin

import httpx
import logging
from bs4 import BeautifulSoup, Tag

from app.models import Author, Quote

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


BASE_URL = "https://quotes.toscrape.com/"

QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]

author_cache = {}


def get_page_soup(url: str, client: httpx.Client) -> BeautifulSoup:
    resp = client.get(url, follow_redirects=True)
    soup = BeautifulSoup(resp.content, "html.parser")
    return soup


def parse_quote(quote_tag: Tag) -> Quote:
    quote_text = quote_tag.select_one(".text")
    quote_author = quote_tag.select_one(".author")
    tags = quote_tag.select(".tag")

    if quote_text is None:
        raise ValueError("Quote text is None")

    if quote_author is None:
        raise ValueError("Quote author is None")

    return Quote(
        text=quote_text.text,
        author=quote_author.text,
        tags=[tag.text for tag in tags],
    )


def parse_quotes_from_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_quote(quote) for quote in quotes]


def parse_author(url: str, client: httpx.Client) -> Author:
    soup = get_page_soup(url, client)

    author_title = soup.select_one(".author-title")
    author_born_date = soup.select_one(".author-born-date")
    author_born_location = soup.select_one(".author-born-location")

    if author_title is None:
        raise ValueError("Author name is None")

    if author_born_date is None:
        raise ValueError("Author date of birth is None")

    if author_born_location is None:
        raise ValueError("Author location is None")

    return Author(
        name=author_title.text,
        born=datetime.strptime(author_born_date.text, "%B %d, %Y").date(),
        location=author_born_location.text.lstrip("in "),
    )


def parse_authors_from_page(
    page_soup: BeautifulSoup, client: httpx.Client
) -> list[Author]:
    authors = []
    authors_data = page_soup.select("span:has(small.author)")
    for author_data in authors_data:
        author_name = author_data.select_one("small.author")
        author_link = author_data.select_one("a")

        if author_name is None or author_link is None:
            raise ValueError("Missing author data")

        if not (author := author_cache.get(author_name.text)):
            request_url = urljoin(BASE_URL, author_link["href"])
            author = parse_author(request_url, client)
            author_cache[author_name.text] = author
            authors.append(author)
    return authors


def get_next_page(page_soup: BeautifulSoup) -> str | None:
    next_tag = page_soup.select_one("ul.pager > li.next > a")
    return (
        urljoin(BASE_URL, next_tag["href"]) if next_tag else None
    )


def write_to_csv(objects: list, csv_path: str, fields: list[str]) -> None:
    with open(csv_path, "w", newline="") as csvfile:
        quotewriter = writer(csvfile)
        quotewriter.writerow(fields)
        quotewriter.writerows(astuple(obj) for obj in objects)


def main(
    quotes_output_csv_path: str = "quotes.csv",
    authors_output_csv_path: str = "authors.csv",
) -> None:
    quotes, authors = [], []
    with httpx.Client() as client:
        next_page = BASE_URL
        while next_page:
            soup = get_page_soup(next_page, client)
            quotes += parse_quotes_from_page(soup)
            authors += parse_authors_from_page(soup, client)
            next_page = get_next_page(soup)

    write_to_csv(quotes, quotes_output_csv_path, QUOTE_FIELDS)
    write_to_csv(authors, authors_output_csv_path, AUTHOR_FIELDS)


if __name__ == "__main__":
    main("quotes.csv", "authors.csv")
