import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.quotes_dto import Quote


BASE_URL = "https://quotes.toscrape.com/"


def parse_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def next_page(page_soup: BeautifulSoup) -> BeautifulSoup | None:
    return page_soup.select_one(".next")


def get_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    all_quotes = get_page_quotes(soup)
    page_num = 1

    while next_page(soup):
        logging.info(f"Parsing #{page_num} page")
        page = requests.get(urljoin(BASE_URL, f"page/{page_num}")).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes += get_page_quotes(soup)
        page_num += 1

    return all_quotes