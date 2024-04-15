from dataclasses import fields, dataclass
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.utils import next_existing_page

BASE_URL = "https://quotes.toscrape.com/"

QUOTES_OUTPUT_CSV_PATH = "quotes.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    tags = [tag.text for tag in quote_soup.select(".tags > a")]
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=tags
    )


def parse_quotes() -> List[Quote]:
    scrapped_quotes = []
    page = 1

    while True:
        response = requests.get(urljoin(BASE_URL, f"page/{page}/")).content
        soup = BeautifulSoup(response, "html.parser")

        quotes = soup.select(".quote")

        scrapped_quotes_on_page = [
            parse_single_quote(quote_soup) for quote_soup in quotes
        ]
        scrapped_quotes.extend(scrapped_quotes_on_page)

        if not next_existing_page(soup):
            break

        page += 1

    return scrapped_quotes
