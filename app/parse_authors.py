import httpx

from bs4 import BeautifulSoup
from dataclasses import dataclass, fields
from datetime import datetime, date


@dataclass
class Author:
    full_name: str
    born_date: date
    born_location: str
    description: str


AUTHOR_FIELDS = [field.name for field in fields(Author)]

cache = {}


def parse_single_author(author_soup: BeautifulSoup) -> Author:
    born_date_str = author_soup.select_one(".author-born-date").text
    born_date = datetime.strptime(born_date_str, "%B %d, %Y").date()

    raw_born_location = author_soup.select_one(".author-born-location").text
    born_location = " ".join(raw_born_location.split()[1:])

    return Author(
        full_name=author_soup.select_one(".author-title").text,
        born_date=born_date,
        born_location=born_location,
        description=author_soup.select_one(".author-description").text.strip()
    )


def parse_author(url: str) -> list[Author]:
    if url in cache.keys():
        return cache[url]

    with httpx.Client() as client:
        page = client.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        author = parse_single_author(soup)

        cache[url] = author


def find_author_url(author_soup: BeautifulSoup) -> str:
    return author_soup.select("span > a")[0].get("href")


def get_all_authors() -> list[Author]:
    return [author for author in cache.values()]
