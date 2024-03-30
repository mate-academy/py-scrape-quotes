import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"

BASE_AUTHOR_URL = urljoin(BASE_URL, "author/")

AUTHOR_CACHE: dict[str, "Author"] = {}

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


@dataclass
class Author:
    name: str
    born_date: str
    born_location: str
    description: str


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_author(author_name: str, author_url: str) -> None:
    if author_name not in AUTHOR_CACHE:

        logging.info(f"Starting parsing page with author {author_name}")
        page = requests.get(urljoin(BASE_URL, author_url)).content
        soup = BeautifulSoup(page, "html.parser")
        print(soup.select(".author-born"))
        author = Author(
            name=soup.select_one(".author-title").text,
            born_date=soup.select_one(".author-born-date").text,
            born_location=soup.select_one(".author-born-location").text,
            description=soup.select_one(".author-description").text
        )
        AUTHOR_CACHE[author_name] = author

    else:
        logging.info(f"Getting author {author_name} from cache")


def parse_single_quote(quote_soup: Tag) -> Quote:
    author_name = quote_soup.select_one(".author").text
    author_url = quote_soup.select_one("a")["href"]
    parse_single_author(author_name, author_url)
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=author_name,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def is_next_page(page_soup: BeautifulSoup) -> bool:
    return bool(page_soup.select_one(".next"))


def get_all_quotes_and_authors() -> list[Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(soup)

    page_number = 1

    while is_next_page(soup):
        page_number += 1
        logging.info(f"Starting parsing page #{page_number}")
        page = requests.get(urljoin(BASE_URL, f"page/{page_number}")).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))

    return all_quotes


def write_authors_to_csv(csv_path: str = "authors.csv") -> None:
    with open(csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Author)])
        writer.writerows([astuple(author) for author in AUTHOR_CACHE.values()])


def write_quotes_to_csv(csv_path: str, quotes: list[Quote]) -> None:
    with open(csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes_and_authors()
    write_quotes_to_csv(output_csv_path, quotes)
    write_authors_to_csv()


if __name__ == "__main__":
    main("quotes.csv")
