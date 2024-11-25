import csv
import logging
import sys
import requests

from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    biography: str


QUOTE_FIELDS = [fields.name for fields in fields(Quote)]
AUTHORS_LIST = set()


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout)
    ],
)


def parse_single_quote(soup: Tag) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=[tag.text for tag in soup.select("a.tag")],
    )


def parse_single_author(soup: Tag) -> Author:
    return Author(
        name=soup.select_one("h3.author-title").text,
        biography=soup.select_one(".author-description").text,
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes_tag = page_soup.select(".quote")
    quotes_list = []
    for quote in quotes_tag:
        quotes_list.append(parse_single_quote(quote))
        author_href = quote.select_one("small.author + a").attrs["href"]
        AUTHORS_LIST.add(author_href)
    return quotes_list


def get_all_pages_quotes() -> list[Quote]:
    logging.info("Start parsing quotes")
    text = requests.get(BASE_URL).content
    soup = BeautifulSoup(text, "html.parser")
    all_quotes = get_single_page_quotes(soup)
    page_no: int = 1

    while True:
        page_no += 1
        logging.info(f"Parsing page #{page_no}")
        text = requests.get(f"{BASE_URL}page/{page_no}").content
        soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        if soup.select_one(".pager > .next") is None:
            break

    return all_quotes


def get_all_pages_authors() -> list[Author]:
    all_authors = []
    for author in AUTHORS_LIST:
        logging.info(f"Start parsing data for "
                     f"{author.replace('/author/', '')}")
        text = requests.get(urljoin(BASE_URL, author)).content
        soup = BeautifulSoup(text, "html.parser")
        all_authors.append(parse_single_author(soup))
    return all_authors


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_authors_to_csv(authors: list[Author]) -> None:
    with open("authors_biography.csv", "a") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows([astuple(author) for author in authors])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(output_csv_path, get_all_pages_quotes())
    write_authors_to_csv(get_all_pages_authors())


if __name__ == "__main__":
    main("quotes.csv")
