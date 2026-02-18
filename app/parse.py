import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


PRODUCT_FIELDS = [field.name for field in fields(Quote)]


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


def parse_single_quote(quote: Tag) -> Quote:
    text_el = quote.select_one(".text")
    text = text_el.get_text(strip=True) if text_el else ""

    author_el = quote.select_one(".author")
    author = author_el.get_text(strip=True) if author_el else "Unknown"

    tags_elements = quote.select(".tags .tag")
    tags = [t.get_text(strip=True) for t in tags_elements]

    return Quote(text=text, author=author, tags=tags)


def get_home_quotes() -> [Quote]:
    text = requests.get(BASE_URL).content
    soup = BeautifulSoup(text, "html.parser")
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_num_pages(page_soup: Tag) -> int:
    pagination = page_soup.select_one(".pagination")
    if pagination is None:
        return 1
    return int(pagination.select("li")[-2].text)


def get_single_page_quotes(page_soup: Tag) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_each_page_quotes() -> list[Quote]:
    logging.info("Start parsing quotes")
    all_quotes = []
    current_page_url = BASE_URL

    while current_page_url:
        logging.info(f"Parsing page: {current_page_url}")

        response = requests.get(current_page_url)
        soup = BeautifulSoup(response.content, "html.parser")

        page_quotes = get_single_page_quotes(soup)
        all_quotes.extend(page_quotes)

        next_button = soup.select_one(".next a")
        if next_button:
            current_page_url = urljoin(BASE_URL, next_button["href"])
        else:
            current_page_url = None

    return all_quotes


def write_quotes_to_csv(
        quotes: list[Quote],
        output_path: str
) -> None:
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_each_page_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
