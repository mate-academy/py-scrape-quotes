from datetime import datetime
from typing import List

import requests
from bs4 import Tag, BeautifulSoup

from app.author import Author
from app.utils import BASE_URL, get_all_items

PARSED_AUTHORS = set()


def parse_single_author(author: Tag) -> Author:
    return Author(
        name=author.select_one(".author-title").text,
        birth_date=datetime.strptime(
            author.select_one(".author-born-date").text, "%B %d, %Y"
        ),
        birth_location=author.select_one(".author-born-location").text[3:],
        description=author.select_one(".author-description").text,
    )


def get_single_author(page_soup: Tag) -> Author:
    author = page_soup.select_one(".author-details")
    return parse_single_author(author)


def get_authors_by_page(page_soup: Tag) -> List[Author]:
    authors = []
    for quote in page_soup.select("div.quote"):
        span = quote.select("span")[-1]

        author = span.select_one(".author").get_text(strip=True)
        if author in PARSED_AUTHORS:
            continue
        PARSED_AUTHORS.add(author)

        href = span.select_one("a").get("href")[1:]

        try:
            response = requests.get(f"{BASE_URL}{href}")
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error {e}")
            continue

        author_page_soup = BeautifulSoup(response.content, "html.parser")
        authors.append(get_single_author(author_page_soup))
    return authors


def get_authors() -> List[Author]:
    return get_all_items(get_authors_by_page)
