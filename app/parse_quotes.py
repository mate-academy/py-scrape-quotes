from bs4 import BeautifulSoup
from dataclasses import fields, dataclass

from .helper import scrape_data


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def create_quote(quote_soup: BeautifulSoup) -> Quote:
    tags = quote_soup.select(".tag")
    return Quote(
        text=quote_soup.select_one(".text").string,
        author=quote_soup.select_one(".author").string,
        tags=[tag.string for tag in tags],
    )


@scrape_data
def get_quotes_from_page(page_soup: BeautifulSoup) -> [Quote]:
    soup_quotes = page_soup.select(".quote")
    return [create_quote(quote_soup) for quote_soup in soup_quotes]
