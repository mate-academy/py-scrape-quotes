import csv
from dataclasses import dataclass, fields, astuple
from functools import cache
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

HOME_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


PRODUCT_FIELDS = [field.name for field in fields(Quote)]

AUTHORS_BIO: dict[str, str] = {}


def get_soup(url: str) -> BeautifulSoup:
    return BeautifulSoup(requests.get(url).content, "html.parser")


def get_all_quotes_tags() -> list[Tag]:
    page_number = 1
    all_quotes = []
    while True:
        url = urljoin(HOME_URL, f"/page/{page_number}")
        soup = get_soup(url)

        quotes = get_quotes_from_page(soup)
        if not quotes:
            break

        all_quotes.extend(quotes)
        page_number += 1
    return all_quotes


@cache
def get_author_bio(author_url: str) -> str:
    bio_soup = get_soup(author_url)
    return bio_soup.select_one(".author-description").text.strip()


def parse_single_quote(quote: Tag) -> Quote:
    author = quote.select_one("[itemprop='author']").text
    author_url = urljoin(
        HOME_URL, quote.select_one("a[href^='/author/']")["href"]
    )
    AUTHORS_BIO[author] = get_author_bio(author_url)
    return Quote(
        text=quote.select_one("[itemprop='text']").text,
        author=author,
        tags=[tag.text for tag in quote.select(".tags a.tag")],
    )


def get_quotes_from_page(soup: BeautifulSoup) -> list[Tag]:
    quotes = soup.select(".quote")
    return quotes


def get_quotes_objects() -> list[Quote]:
    return [parse_single_quote(quote) for quote in get_all_quotes_tags()]


def write_to_csv(name: str) -> None:
    with open(name, "w") as file:
        writer = csv.writer(file)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows([astuple(quote) for quote in get_quotes_objects()])


def write_to_csv_author_bio(name: str) -> None:
    with open(name, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["author", "biography"])
        writer.writerows(AUTHORS_BIO.items())


def main(output_csv_path: str) -> None:
    write_to_csv(output_csv_path)
    write_to_csv_author_bio("authors_bio.csv")


if __name__ == "__main__":
    main("quotes.csv")
