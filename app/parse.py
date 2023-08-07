import csv
import logging
import sys

from dataclasses import dataclass, fields, astuple
from pprint import pprint

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "http://quotes.toscrape.com/"
OUTPUT_CSV_PATH = "quotes_data.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(single_quote: Tag) -> Quote:
    single_quote_data = dict(
        text=single_quote.select_one("span.text").text,
        author=single_quote.select_one(".author").text,
        tags=[tag.text for tag in single_quote.find_all("a", class_="tag")]
    )
    return Quote(**single_quote_data)


def parse_quotes_of_one_page() -> list[Quote]:
    page_content = requests.get(BASE_URL).content
    base_soup = BeautifulSoup(page_content, "html.parser")

    page_quotes_soup = base_soup.select(".quote")
    print(page_quotes_soup)

    all_page_quotes = [
        parse_single_quote(single_quote) for single_quote in page_quotes_soup
    ]
    pprint(all_page_quotes)

    return all_page_quotes


def parse_all_quotes() -> list[Quote]:
    page_content = requests.get(BASE_URL).content
    base_soup = BeautifulSoup(page_content, "html.parser")

    page_quotes_soup = base_soup.select(".quote")

    all_page_quotes = [
        parse_single_quote(single_quote) for single_quote in page_quotes_soup
    ]
    pprint(all_page_quotes)

    return all_page_quotes


def write_quotes_to_csv(
        quotes: list[Quote],
        output_path: str = OUTPUT_CSV_PATH,
) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str = OUTPUT_CSV_PATH) -> None:
    quotes = parse_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
