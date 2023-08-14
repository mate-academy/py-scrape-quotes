from __future__ import annotations

import csv
import logging
import requests
import sys

from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup, Tag


BASE_URL = "http://quotes.toscrape.com/"
OUTPUT_QUOTES_CSV_PATH = "quotes_data.csv"
OUTPUT_AUTHORS_CSV_PATH = "authors_data.csv"


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    @classmethod
    def parse_single_quote(cls, single_quote: Tag) -> Quote:
        single_quote_data = dict(
            text=single_quote.select_one("span.text").text,
            author=single_quote.select_one(".author").text,
            tags=[
                tag.text for tag in single_quote.find_all("a", class_="tag")
            ],
        )
        return cls(**single_quote_data)


@dataclass
class Author:
    name: str
    biography: str

    @classmethod
    def parse_single_author(
            cls,
            author_url: str,
            author_cache: dict[str: Author]
    ) -> Author:
        if author_url in author_cache:
            return author_cache[author_url]

        author_response = requests.get(author_url)
        author_soup = BeautifulSoup(author_response.content, "html.parser")
        author_name = author_soup.select_one("h3.author-title").text
        author_biography = author_soup.find(
            "div", class_="author-description"
        ).text.strip()

        author = Author(name=author_name, biography=author_biography)
        author_cache[author_url] = author

        return author


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


def parse_single_page(
        page_url: str,
        author_cache: dict[str: Author],
) -> tuple[list[Quote], list[Author]]:
    page_content = requests.get(page_url).content
    base_soup = BeautifulSoup(page_content, "html.parser")

    page_quotes_soup = base_soup.select(".quote")

    quotes_list = []
    author_list = []

    for single_quote in page_quotes_soup:
        quote = Quote.parse_single_quote(single_quote)

        author_url_element = single_quote.find(
            "small", class_="author"
        ).find_next("a")
        if author_url_element:
            author_url = BASE_URL + author_url_element["href"]
            author = Author.parse_single_author(author_url, author_cache)
            quotes_list.append(quote)
            author_list.append(author)

    return quotes_list, author_list


def parse_all_pages() -> tuple[list[Quote], list[Author]]:
    logging.info("Start parsing quotes\n________________________________\n")

    all_quotes_list = []
    all_author_list = []
    page = 1
    author_cache = {}

    while True:
        logging.info(f"Start parsing page №: {page}")

        page_url = f"{BASE_URL}page/{page}/"
        parsed_quotes_list, parsed_author_list = (
            parse_single_page(page_url, author_cache)
        )

        if not parsed_quotes_list:
            logging.info(
                "________________________\n"
                "Parsing is finished successfully\n"
            )
            break

        all_quotes_list.extend(parsed_quotes_list)
        all_author_list.extend(parsed_author_list)
        page += 1

    return all_quotes_list, all_author_list


def write_data_to_csv(
        data_list: list[Quote] | list[Author],
        output_path: str,
        fields_list: list[str],
) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(fields_list)
        writer.writerows([astuple(element) for element in data_list])


def main(
        output_quotes_csv_path: str = OUTPUT_QUOTES_CSV_PATH,
        output_authors_csv_path: str = OUTPUT_AUTHORS_CSV_PATH
) -> None:
    all_quotes_list, all_author_list = parse_all_pages()
    write_data_to_csv(all_quotes_list, output_quotes_csv_path, QUOTE_FIELDS)
    write_data_to_csv(all_author_list, output_authors_csv_path, AUTHOR_FIELDS)


if __name__ == "__main__":
    main("quotes.csv")
