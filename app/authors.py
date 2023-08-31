import requests

from dataclasses import dataclass
from bs4 import BeautifulSoup


@dataclass
class Author:
    name: str
    birth_date: str
    birth_place: str
    biography: str


def parse_author(author_url: str) -> Author:
    author_page = requests.get(author_url).content
    author_soup = BeautifulSoup(author_page, "html.parser")
    return Author(
        name=author_soup.select_one(".author-title").text.strip(),
        birth_date=author_soup.select_one(".author-born-date").text,
        birth_place=author_soup.select_one(".author-born-location").text,
        biography=author_soup.select_one(
            ".author-description"
        ).text.strip().replace("\n", "")
    )
