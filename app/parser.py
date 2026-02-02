from bs4 import Tag, BeautifulSoup

from app.config import Quote, Author


def parse_single_quote(quote: Tag) -> Quote:
    return Quote (
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=quote.select_one("meta.keywords")["content"].split(",")
    )


def parse_single_author(author: BeautifulSoup) -> Author:
    return Author(
        name=author.select_one(".author-title").text,
        birth_date=author.select_one(".author-born-date").text,
        birth_location=author.select_one(".author-born-location").text[3:],
        biography=author.select_one(".author-description").text.strip(),
    )
