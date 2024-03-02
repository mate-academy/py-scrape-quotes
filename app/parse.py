import csv
import logging
import sys
import time
import random
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin


import requests
from bs4 import BeautifulSoup

HOME_URL = "https://quotes.toscrape.com/"

PAGE_URL = urljoin(HOME_URL, "page/")

AUTHOR_URL = urljoin(HOME_URL, "author/")


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


CSV_FIELDS_QUOTE = [field.name for field in fields(Quote)]


@dataclass
class Author:
    name: str
    born_date: str
    born_place: str
    description: str


CSV_FIELDS_AUTHOR = [field.name for field in fields(Author)]


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


def get_author_urls(quote_soup: BeautifulSoup) -> str:

    return quote_soup.select_one("a")["href"]


def get_single_page_authors(page_soup: BeautifulSoup) -> list:
    quotes = page_soup.select(".quote")

    return [get_author_urls(page_soup) for page_soup in quotes]


def parse_single_author(author_soup: BeautifulSoup) -> Author:

    return Author(
        name=author_soup.select_one(".author-title").text,
        born_date=author_soup.select_one(".author-born-date").text,
        born_place=author_soup.select_one(".author-born-location").text[3:],
        description=author_soup.select_one(".author-description").text.strip(),
    )


def get_authors_info(urls: set) -> [Author]:
    logging.info("Start of authors parsing")

    all_authors = []

    for url in urls:
        time.sleep(random.randint(1, 3))

        page_url = urljoin(HOME_URL, url)
        logging.info(f"Parsing info from {page_url}")
        page = requests.get(page_url).content
        page_soup = BeautifulSoup(page, "html.parser")

        all_authors.append(parse_single_author(page_soup))

    logging.info(f"Collected info about {len(all_authors)} authors")

    return all_authors


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:

    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select("a.tag")],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(page_soup) for page_soup in quotes]


def get_quotes() -> [Quote]:
    logging.info("Start of quotes parsing")

    all_quotes = []
    all_authors_urls = []

    page_num = 1
    current_page_url = urljoin(PAGE_URL, str(page_num))
    logging.info(current_page_url)
    first_page = requests.get(current_page_url).content
    first_page_soup = BeautifulSoup(first_page, "html.parser")
    present_next = first_page_soup.select_one(".next").text

    while present_next:
        logging.info(
            f"Requesting page {current_page_url} : status: {requests.get(current_page_url).status_code}"
        )
        time.sleep(random.randint(1, 5))

        page = requests.get(current_page_url).content
        page_soup = BeautifulSoup(page, "html.parser")

        all_quotes.extend(get_single_page_quotes(page_soup))
        all_authors_urls.extend(get_single_page_authors(page_soup))

        present_next = page_soup.select_one(".next")

        page_num += 1
        current_page_url = urljoin(PAGE_URL, str(page_num))

    return all_quotes, set(all_authors_urls)


def output_as_csv(path, objs: list, csv_fields: list) -> None:
    with open(
        path,
        "w",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(csv_fields)
        writer.writerows([astuple(obj) for obj in objs])

    logging.info(f"Saved {len(objs)} objects to {path}.")


def main(output_csv_path: str) -> None:
    results = get_quotes()
    quotes = results[0]
    authors = get_authors_info(results[1])
    output_as_csv(output_csv_path, quotes, CSV_FIELDS_QUOTE)
    output_as_csv("authors.csv", authors, CSV_FIELDS_AUTHOR)


if __name__ == "__main__":
    main("quotes.csv")
