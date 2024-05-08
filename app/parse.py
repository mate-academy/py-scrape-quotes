import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"

AUTHOR_CACHE: dict[str, "Author"] = {}


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


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s] %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


def parse_single_author(author_name: str, author_url: str) -> None:
    if author_name not in AUTHOR_CACHE:
        page = requests.get(urljoin(BASE_URL, author_url))
        soup = BeautifulSoup(page.content, "html.parser")
        author = Author(
            name=soup.select_one(".author-title").text,
            born_date=soup.select_one(".author-born-date").text,
            born_location=soup.select_one(".author-born-location").text,
            description=soup.select_one(".author-description").text,
        )
        AUTHOR_CACHE[author_name] = author
    else:
        logging.info(f"Getting author {author_name} from cache")


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    author_name = quote_soup.select_one(".author").text
    author_url = quote_soup.select_one("a")["href"]
    parse_single_author(author_name, author_url)
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=author_name,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def is_next_page(page_soup: BeautifulSoup) -> bool:
    return bool(page_soup.select_one(".next"))


def get_quotes() -> [Quote]:
    logging.info("Start parsing Quotes")
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    all_quotes = get_single_page_quotes(soup)
    page_num = 1

    while is_next_page(soup):
        page_num += 1
        logging.info(f"Start parsing page {page_num}")
        page = requests.get(urljoin(BASE_URL, f"page/{page_num}/")).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))

    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: [Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_author_to_csv(csv_path: str) -> None:
    with open(csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows([astuple(author) for author in AUTHOR_CACHE.values()])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(output_csv_path, quotes)
    write_author_to_csv("author.csv")


if __name__ == "__main__":
    main("quotes.csv")
