import csv
import os

import requests

from bs4 import BeautifulSoup, Tag

from app.description import Quote, CLASS_QUOTE, HTML_PARSER, QUOTE_FIELD_NAMES


def write_quote_to_file(file_name: str, quote: Quote) -> None:
    file_exists = os.path.exists(file_name)

    with open(file_name, "a+", newline="", encoding="utf-8") as quote_file:

        quote_writer = csv.DictWriter(quote_file, fieldnames=QUOTE_FIELD_NAMES)

        if not file_exists:
            quote_writer.writeheader()

        quote_writer.writerow(quote.__dict__)


def parse_single_quote(quot_soup: Tag) -> Quote:
    return Quote(
        text=quot_soup.select_one(".text").text,
        author=quot_soup.select_one(".author").text,
        tags=[
            tag.text for tag in quot_soup.select(".tags .tag")
        ]
    )


def get_quotes_from_page(soup: BeautifulSoup) -> [Quote]:
    quotes = soup.select(CLASS_QUOTE)

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quote_from_all_pages(base_url: str, ext_url: str) -> [Quote]:
    page = requests.get(base_url).content
    soup = BeautifulSoup(page, HTML_PARSER)

    all_quote_in_site = get_quotes_from_page(soup)
    page_counter = 2

    while soup.select(".next"):
        page = requests.get(ext_url + f"{page_counter}/").content
        soup = BeautifulSoup(page, HTML_PARSER)

        all_quote_in_site.extend(get_quotes_from_page(soup))

        page_counter += 1

    return all_quote_in_site
