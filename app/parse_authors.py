import requests
import csv
from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Author:
    name: str
    bio: str


AUTHOR_FIELDS = [field.name for field in fields(Author)]

authors_cache = {}


def get_one_author_info(author_url: str) -> Author:
    existing_author = authors_cache.get(author_url)
    if existing_author:
        new_author = Author(**existing_author)
    else:
        new_url = urljoin(BASE_URL, author_url)
        response = requests.get(new_url).content
        new_page_soup = BeautifulSoup(response, "html.parser")
        new_author = Author(
            name=new_page_soup.select_one(".author-title").text,
            bio=new_page_soup.select_one(".author-description").text.strip(),
        )
        authors_cache[author_url] = {
            "name": new_author.name,
            "bio": new_author.bio
        }
    return new_author


def get_authors_urls_per_page(page_soup: BeautifulSoup) -> list:
    quotes = page_soup.select(".quote")
    authors_urls = [quote.select_one(" a")["href"] for quote in quotes]
    return authors_urls


def get_all_authors_urls() -> set:
    response = requests.get(BASE_URL).content
    page_soup = BeautifulSoup(response, "html.parser")
    all_authors_urls = set(get_authors_urls_per_page(page_soup))

    next_tag = page_soup.select_one("li.next a")
    pagination = next_tag["href"] if next_tag else None

    while pagination is not None:
        new_url = urljoin(BASE_URL, pagination)
        response = requests.get(new_url).content
        new_page_soup = BeautifulSoup(response, "html.parser")
        all_authors_urls.update(get_authors_urls_per_page(new_page_soup))
        next_tag = new_page_soup.select_one("li.next a")
        pagination = next_tag["href"] if next_tag else None

    return all_authors_urls


def get_all_authors() -> list:
    all_authors = []
    all_authors_urls = get_all_authors_urls()
    for author_url in all_authors_urls:
        all_authors.append(get_one_author_info(author_url))
    return all_authors


def write_authors_to_csv(authors: list[Author], authors_csv: str) -> None:
    with open(
            authors_csv,
            "w",
            encoding="utf-8",
            newline=""
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows([astuple(author) for author in authors])
