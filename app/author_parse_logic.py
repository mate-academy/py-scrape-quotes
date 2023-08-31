import csv
import os

from datetime import datetime

from bs4 import BeautifulSoup

from app.description import Author
from app.description import CLASS_QUOTE, HTML_PARSER

import requests

from app.description import BASE_URL, CLASS_AUTHOR, AUTHOR_FIELD_NAMES


def write_author_to_file(file_name: str, author: Author) -> None:
    file_exists = os.path.exists(file_name)
    field_names = AUTHOR_FIELD_NAMES

    with open(file_name, "a+", newline="", encoding="utf-8") as author_file:

        author_writer = csv.DictWriter(author_file, fieldnames=field_names)

        if not file_exists:
            author_writer.writeheader()

        author_writer.writerow(author.__dict__)


def insert_author_to_dict(author_soup: BeautifulSoup) -> Author:
    return Author(
        name=author_soup.select_one(".author-title").text,
        born_date=datetime.strptime(
            author_soup.select_one(".author-born-date").text, "%B %d, %Y"
        ),
        born_city=author_soup.select_one(
            ".author-born-location").text.split()[1],
        born_country=author_soup.select_one(
            ".author-born-location").text.split()[2],
        description=author_soup.select_one(
            ".author-description").text,
    )


def get_authors_from_page(soup: BeautifulSoup) -> dict:
    author_dict = {}
    quotes = soup.select(CLASS_QUOTE)

    for quote in quotes:
        author_name = quote.select_one(CLASS_AUTHOR).text
        if author_name not in author_dict:
            author_url = quote.select_one("a")["href"]
            author_page = requests.get(BASE_URL + author_url).content
            author_soup = BeautifulSoup(author_page, HTML_PARSER)
            author_dict[author_name] = insert_author_to_dict(author_soup)

    return author_dict


def get_authors_from_all_pages(base_url: str, ext_url: str) -> dict:
    page = requests.get(base_url).content
    soup = BeautifulSoup(page, HTML_PARSER)

    authors_dict = get_authors_from_page(soup)
    page_counter = 2

    while soup.select(".next"):
        page = requests.get(ext_url + f"{page_counter}/").content
        soup = BeautifulSoup(page, HTML_PARSER)

        authors_dict.update(get_authors_from_page(soup))

        page_counter += 1

    return authors_dict
