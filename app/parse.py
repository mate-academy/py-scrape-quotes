import csv
import time

import requests

from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"
START_URL = "https://quotes.toscrape.com/page/1/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    current_url = START_URL

    while True:
        time.sleep(1)
        text = requests.get(current_url).content
        page_soup = BeautifulSoup(text, features="html.parser")

        page_quotes = get_single_page_quotes(page_soup)
        all_quotes.extend(page_quotes)

        next_link = page_soup.select_one(".next a")

        if next_link is None:
            break

        next_href = next_link["href"]
        current_url = urljoin(BASE_URL, next_href)

    return all_quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in get_all_quotes())


if __name__ == "__main__":
    main("quotes.csv")
