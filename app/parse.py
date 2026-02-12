import time
from dataclasses import dataclass, fields, astuple
import csv
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag
from requests import RequestException

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_block(block: Tag) -> Quote:
    return Quote(
        text=block.select_one(".text").text,
        author=block.select_one(".author").text,
        tags=[tag.text for tag in block.select(".tag")]
    )


def get_all_quotes() -> list[Quote]:
    page = 1
    quotes = []

    while True:
        url = urljoin(BASE_URL, f"page/{page}/")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except RequestException as e:
            print(f"Request failed on page {page}: {e}")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        blocks = soup.select(".quote")

        if not blocks:
            break

        quotes.extend(parse_single_block(block) for block in blocks)
        page += 1
        time.sleep(0.5)

    return quotes


def write_quotes_to_csv(path: str, quotes: list[Quote]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(output_csv_path, get_all_quotes())


if __name__ == "__main__":
    main("quotes.csv")
