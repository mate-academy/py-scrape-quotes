import csv
import sys

import logging
from dataclasses import astuple, dataclass, fields
from typing import Dict, List, Tuple

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


@dataclass
class Author:
    name: str
    bio: str


QUOTES_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout)
    ],
)


def parse_single_quote(quote: Tag) -> Tuple[Quote, Tuple[str, str]]:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags = [tag.text for tag in quote.select(".tag")]
    author_bio_url = quote.select_one("a[href*='/author/']")["href"]
    return Quote(text=text, author=author, tags=tags), (author, author_bio_url)


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    results = page_soup.select(".quote")
    quote_list = []
    author_dict = {}
    for res in results:
        quote, author_info = parse_single_quote(res)
        quote_list.append(quote)
        author_dict[author_info[1]] = author_info[0]

    return quote_list, author_dict


def get_quotes() -> Tuple[List[Quote], Dict[str, str]]:
    logging.info("Getting quotes...")
    text = requests.get(BASE_URL, timeout=5).content
    first_page_soup = BeautifulSoup(text, "html.parser")

    all_quotes, author_dict = get_single_page_quotes(first_page_soup)
    page_number = 2
    while True:
        logging.info(f"Getting quotes from page {page_number}...")
        text = requests.get(
            BASE_URL + f"page/{page_number}",
            timeout=5
        ).content

        next_page_soup = BeautifulSoup(text, "html.parser")
        page_quotes, page_authors = get_single_page_quotes(next_page_soup)
        all_quotes.extend(page_quotes)
        author_dict.update(page_authors)

        if not next_page_soup.select_one(".next"):
            break
        page_number += 1
    return all_quotes, author_dict


def get_authors_bio(author_link: Dict[str, str]) -> List[Author]:
    authors = []
    for key, value in author_link.items():
        logging.info(f"Getting author bio for {value}...")
        text = requests.get(BASE_URL + key, timeout=5).content
        author_soup = BeautifulSoup(text, "html.parser")
        bio = author_soup.select_one(".author-description").text
        authors.append(Author(name=value, bio=bio))
    return authors


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def write_author_bio_to_csv(
        authors: list[Author],
        output_csv_path: str
) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows(astuple(author) for author in authors)


def main(output_csv_path: str) -> None:
    quotes, author_links = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)
    authors = get_authors_bio(author_links)
    write_author_bio_to_csv(authors, "author.csv")


if __name__ == "__main__":
    main("quotes.csv")
