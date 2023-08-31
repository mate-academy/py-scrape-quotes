import requests

from urllib.parse import urljoin
from dataclasses import dataclass
from bs4 import BeautifulSoup

from app.authors import parse_author

BASE_URL = "https://quotes.toscrape.com"
AUTHORS_LIST = []


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    author_url = urljoin(
        BASE_URL,
        quote_soup.select_one(".author + a")["href"]
    )

    author = parse_author(author_url)

    if author not in AUTHORS_LIST:
        AUTHORS_LIST.append(author)

    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.get_text() for tag in quote_soup.find_all("a", class_="tag")]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> [Quote]:
    page_num = 1
    all_quotes = []
    while True:
        page = requests.get(urljoin(BASE_URL, f"/page/{page_num}/")).content
        soup = BeautifulSoup(page, "html.parser")

        all_quotes.extend(get_single_page_quotes(soup))
        page_num += 1
        if not soup.select_one("li.next a"):
            break

    return all_quotes
