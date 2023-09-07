import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.parse import get_pages_number

URL = "https://quotes.toscrape.com/"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


@dataclass
class Author:
    name: str
    birth_date: str
    born_location: str
    biography: str


AUTHORS_FIELDS = [field.name for field in fields(Author)]


def memorize(func):
    cache = {}

    def wrapper(*args):
        if args in cache:
            return cache[args]
        else:
            result = func(*args)
            cache[args] = result
            return result

    return wrapper


def parse_single_author(author_soup: BeautifulSoup) -> Author:
    return Author(
        name=author_soup.select_one(".author-title").text,
        birth_date=author_soup.select_one(".author-born-date").text,
        born_location=author_soup.select_one(".author-born-location").text,
        biography=author_soup.select_one(".author-description").text,
    )


def get_authors_link_from_single_page(page_soup: BeautifulSoup) -> list[str]:
    authors = page_soup.select(".quote > span > a[href*='author']")

    return [author_link.get("href") for author_link in authors]


@memorize
def get_single_biography(name: str) -> Author:
    biography_page = requests.get(urljoin(URL, name)).content
    biography_soup = BeautifulSoup(biography_page, "html.parser")

    author = parse_single_author(biography_soup)
    logging.info(f"Parsing page #{name}...")

    return author


def get_all_authors_biography():
    page = requests.get(URL).content
    page_soup = BeautifulSoup(page, "html.parser")

    num_pages = get_pages_number(page_soup)
    authors_bio_list = []

    for num in range(num_pages + 1):
        logging.info(f"Parsing page #{num}...")

        next_page_url = urljoin(URL, f"/page/{num}/")
        next_page = requests.get(next_page_url).content
        current_page_soup = BeautifulSoup(next_page, "html.parser")

        author_links = get_authors_link_from_single_page(current_page_soup)

        for author_link in author_links:
            biography = get_single_biography(author_link)
            if biography not in authors_bio_list:
                authors_bio_list.append(biography)

    return authors_bio_list


def wright_biography_to_csv(authors: [Author], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(AUTHORS_FIELDS)
        writer.writerows([astuple(author) for author in authors])


def main(output_csv_path: str) -> None:
    authors = get_all_authors_biography()
    wright_biography_to_csv(authors, output_csv_path)


if __name__ == "__main__":
    main("authors.csv")
