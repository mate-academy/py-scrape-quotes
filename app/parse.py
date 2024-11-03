import csv
import logging
import os
import sys
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("parser.log")),
        logging.StreamHandler(sys.stdout),
    ],
)


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    tags_soup = quote.select_one(".tags")
    tags = [tag.text for tag in tags_soup.select(".tag")]
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=tags
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_list_of_quotes() -> list[Quote]:
    logging.info("Start parse")
    quote_page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(quote_page, "html.parser")

    all_quotes = get_single_page_quotes(first_page_soup)
    logging.info("First page was parsed successfully")

    next_btn = first_page_soup.select_one(".next")
    page_num = 1
    while next_btn:
        page_num += 1
        logging.info(f'Parsing page: {urljoin(BASE_URL, f"page/{page_num}/")}')
        quote_page = requests.get(urljoin(
            BASE_URL, f"page/{page_num}/")
        ).content
        soup = BeautifulSoup(quote_page, "html.parser")
        next_btn = soup.select_one(".next")
        all_quotes.extend(get_single_page_quotes(soup))
        logging.info(f"Parsing of page {page_num} was successful")

    return all_quotes


def write_quotes_to_the_file(
        output_csv_path: str,
        quotes: list[Quote]
) -> None:
    with open(output_csv_path, "w", newline="") as file:
        write = csv.writer(file)
        write.writerow(QUOTES_FIELDS)
        write.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_list_of_quotes()
    write_quotes_to_the_file(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
