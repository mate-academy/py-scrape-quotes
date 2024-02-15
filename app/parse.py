import requests
import csv

from typing import Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from dataclasses import dataclass

BASE_URL = "https://quotes.toscrape.com/"

"""
A dictionary to store the full name of the author, as a key
and his URL, as a value.
"""
AUTHORS_URLS = dict()


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELD_NAMES = ["text", "author", "tags"]


@dataclass
class Author:
    full_name: str
    born_date: str
    birth_place: str


AUTHOR_FIELD_NAMES = ["full_name", "born_date", "birth_place"]


def parse_simple_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[soup.text for soup in quote_soup.select(".tag")],
    )


def parse_simple_author(author_soup: BeautifulSoup) -> Author:
    return Author(
        full_name=author_soup.select_one(".author-title").text,
        born_date=author_soup.select_one(".author-born-date").text,
        birth_place=author_soup.select_one(
            ".author-born-location").text.replace("in ", "", 1)
    )


def parse_quotes(quotes_soup: BeautifulSoup) -> list[Quote]:
    return [parse_simple_quote(quote) for quote in quotes_soup]


def get_quotes_soup(url: str) -> (BeautifulSoup, Optional[str]):
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")

    quotes = soup.select("div.quote")

    next_page = soup.select(".pager > .next > a")
    next_page_href = None

    if next_page:
        next_page_href = next_page[0]["href"]

    return quotes, next_page_href


def get_authors_urls(quote_soup: BeautifulSoup) -> None:
    for author in quote_soup:
        full_name = author.select_one(".author").text
        author_url = author.select_one("a")["href"]
        if not AUTHORS_URLS.get("full_name"):
            AUTHORS_URLS[full_name] = author_url


def get_authors_list(
        urls: dict[str, str],
        base_url: str = BASE_URL
) -> list[Author]:
    author_list = []
    for url in urls.values():
        new_url = urljoin(base_url, url)
        page = requests.get(new_url).content
        soup = BeautifulSoup(page, "html.parser")
        author_list.append(parse_simple_author(soup))

    return author_list


def parse(url: str = BASE_URL) -> ([Quote], [Author]):
    quotes_soup, next_page_href = get_quotes_soup(url)
    quotes_list = parse_quotes(quotes_soup)
    get_authors_urls(quotes_soup)

    while next_page_href is not None:
        new_url = urljoin(BASE_URL, next_page_href)
        quotes_soup, next_page_href = get_quotes_soup(new_url)
        quotes_list.extend(parse_quotes(quotes_soup))
        get_authors_urls(quotes_soup)

    author_list = get_authors_list(AUTHORS_URLS)

    return quotes_list, author_list


def write_to_csv(
        data: list[Quote],
        field_names: list[str],
        path_file: str
) -> None:
    with open(path_file, "w", newline="", encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(field_names)
        for instance in data:
            row_data = [getattr(instance, field) for field in field_names]
            writer.writerow(row_data)


def main(output_csv_path: str) -> None:
    quotes, authors = parse(BASE_URL)
    write_to_csv(quotes, QUOTE_FIELD_NAMES, output_csv_path)
    write_to_csv(authors, AUTHOR_FIELD_NAMES, "authors.csv")


if __name__ == "__main__":
    main("quotes.csv")
