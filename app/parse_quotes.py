from typing import List

from bs4 import Tag

from app.quote import Quote
from app.utils import get_all_items


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one("span.text").text,
        author=quote.select_one(".author").text,
        tags=[tag.get_text() for tag in quote.select(".tag")],
    )


def get_quotes_by_page(page_soup: Tag) -> List[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> List[Quote]:
    return get_all_items(get_quotes_by_page)
