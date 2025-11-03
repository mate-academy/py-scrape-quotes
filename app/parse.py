import logging
import time
from dataclasses import dataclass, fields, astuple
import csv
from typing import List

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


logger = logging.getLogger(__name__)
BASE_URL = "https://quotes.toscrape.com/"
QUOTE_FIELDS = fields(Quote)


def write_csv_file(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([field.name for field in QUOTE_FIELDS])
        writer.writerows([astuple(quote) for quote in quotes])


def parse_quote(soup: Tag) -> Quote:
    tags = soup.select_one(".tags")
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=[tag.text for tag in tags.select(".tag")]
    )


def retrieve_quotes(soup: Tag) -> List[Quote]:
    quotes = soup.select(".quote")
    quotes_result = []
    for quote in quotes:
        quotes_result.append(parse_quote(quote))
    return quotes_result


def get_soup(url: str) -> Tag:
    text = requests.get(url).content
    soup = BeautifulSoup(text, "html.parser")
    return soup


def main(output_csv_path: str) -> None:
    logging.basicConfig(level=logging.INFO)
    soup = get_soup(BASE_URL)
    quotes = retrieve_quotes(soup)
    page_num = 2
    while soup.select_one(".next") is not None:
        time.sleep(1)
        logger.info(f"Current page: {page_num}")
        soup = get_soup(f"{BASE_URL}/page/{page_num}")
        quotes.extend(retrieve_quotes(soup))
        page_num += 1
    write_csv_file(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
