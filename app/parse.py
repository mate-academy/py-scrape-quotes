import csv
import sys
from dataclasses import dataclass, fields, astuple
import logging
from urllib.parse import urljoin

import requests
from bs4 import Tag, BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("parser.log")
    ],
)

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_quotes(url: str) -> list[Quote]:
    result = []
    logging.info(f"Getting quotes from {url}")
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    result.extend(get_single_page(soup))

    page_num = 2
    while soup.select_one(".next"):
        url = urljoin(url, f"/page/{page_num}/")
        logging.info(f"Getting quotes from {url}")
        page = requests.get(url, {"page": page_num}).content
        soup = BeautifulSoup(page, "html.parser")
        result.extend(get_single_page(soup))
        page_num += 1
    return result


def get_single_page(soup: BeautifulSoup) -> list[Quote]:
    page_data = []
    for tag in soup.select(".quote"):
        page_data.append(get_single_tag(tag))
    return page_data


def get_single_tag(page: Tag) -> Quote:
    text = page.select_one(".text").text
    author = page.select_one(".author").text
    tags = [tag.text for tag in page.select(".tag")]
    return Quote(text, author, tags)


def save_quotes(filename: str, quotes: list[Quote]) -> None:
    logging.info(f"Saving quotes to {filename}")
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])
    logging.info(f"Saved {len(quotes)} quotes to {filename}")
    return


def main(output_csv_path: str) -> None:
    quotes = get_quotes(BASE_URL)
    save_quotes(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
