import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple

from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag
import requests

BASE_URL = "https://quotes.toscrape.com/"


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ]
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


bio_authors = {}


def check_and_add_author_bio(author: str, link_bio: str) -> None:
    global bio_authors

    if author not in bio_authors:
        url = urljoin(BASE_URL, link_bio)
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        text = resp.content

        author_page = BeautifulSoup(text, "html.parser")

        bio_authors[author] = (author_page.select_one(
            ".author-description"
        ).text).replace("\n", "").strip()


def parse_one_quote(quote: Tag) -> Quote:
    author = quote.select_one(".author").text
    link_bio = quote.find(
        "small", class_="author"
    ).find_next_sibling("a")["href"]

    check_and_add_author_bio(author, link_bio)

    tags_str = quote.select_one(".tags meta")["content"]
    tags = tags_str.split(",") if tags_str else []

    return Quote(
        text=quote.select_one(".quote .text").text,
        author=author,
        tags=tags
    )


def get_one_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_one_quote(quote) for quote in quotes]


def parse_pages_quotes() -> list[Quote]:
    logging.info("Start parsing page number: /page/1/")
    text = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(text, "html.parser")

    all_quotes = get_one_page_quotes(first_page_soup)

    # get part of url of next page
    next_page_url = first_page_soup.select_one(".next a")["href"]

    while True:
        logging.info(f"Start parsing page number: {next_page_url}")
        url = urljoin(BASE_URL, next_page_url)
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        text = resp.content

        page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_one_page_quotes(page_soup))

        next_link = page_soup.select_one(".next a")
        if not next_link:
            break
        next_page_url = next_link["href"]

    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_bio_authors() -> None:
    with open("authors_bio.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["author", "author description"])
        writer.writerows([[key, value] for key, value in bio_authors.items()])


def main(output_csv_path: str) -> None:

    write_quotes_to_csv(output_csv_path, parse_pages_quotes())

    write_bio_authors()


if __name__ == "__main__":
    main("quotes.csv")
