import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from typing import Type
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]:   %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    bio: str

    authors_links = set()
    authors = []


def get_obj_fields(obj: Type[Quote | Author]) -> [str]:
    return [field.name for field in fields(obj)]


def get_page_soup(url: str) -> BeautifulSoup:
    page = requests.get(url).content
    return BeautifulSoup(page, "html.parser")


def parse_author(author_soup: BeautifulSoup) -> Author:
    return Author(
        name=author_soup.select_one(".author-title").text.split("\n")[0],
        bio=author_soup.select_one(".author-description").text.strip("\n"),
    )


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    author_link = quote_soup.select_one("a")["href"]
    if author_link not in Author.authors_links:
        Author.authors_links.add(author_link)
        author_soup = get_page_soup(urljoin(BASE_URL, author_link))
        author = parse_author(author_soup)
        Author.authors.append(author)
        logging.info(f"Author {author.name} parsed")
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def parse_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quote_soups = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quote_soups]


def button_next_exist(soup: BeautifulSoup) -> bool:
    button_next = soup.select_one(".next")
    return True if button_next else False


def write_obj_to_csv(
    output_csv_path: str, all_obj: [Quote | Author], obj: Type[Author | Quote]
) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(get_obj_fields(obj))
        writer.writerows([astuple(obj) for obj in all_obj])


def main(output_quote_csv_path: str) -> None:
    logging.info("Start parsing quotes")
    page_soup = get_page_soup(BASE_URL)
    page_num = 1
    all_quotes = []

    while button_next_exist(page_soup):
        logging.info(f"Start parsing page number #{page_num}")
        all_quotes.extend(parse_single_page_quotes(page_soup))
        page_num += 1
        page_soup = get_page_soup(urljoin(BASE_URL, f"/page/{page_num}/"))

    logging.info(f"Start parsing page number #{page_num}")
    all_quotes.extend(parse_single_page_quotes(page_soup))

    write_obj_to_csv(output_quote_csv_path, all_quotes, Quote)
    write_obj_to_csv("authors.csv", Author.authors, Author)


if __name__ == "__main__":
    main("quotes.csv")
