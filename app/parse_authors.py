import pickle
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from dataclasses import dataclass, fields

from .helper import scrape_data, BASE_QUOTES_URL


AUTHOR_CASH_FILE = "author_cash.pickle"


@dataclass
class Author:
    full_name: str
    born_date: str
    born_location: str
    biography: str


AUTHORS_FIELDS = [field.name for field in fields(Author)]


def load_authors_cash() -> set:
    try:
        with open(AUTHOR_CASH_FILE, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return set()


def save_authors_cash(author_cash: set) -> None:
    with open(AUTHOR_CASH_FILE, "wb") as file:
        pickle.dump(author_cash, file)


def create_author(author_soup: BeautifulSoup) -> Author:
    author = Author(
        full_name=author_soup.select_one(".author-title").string,
        born_date=author_soup.select_one(".author-born-date").string,
        born_location=author_soup.select_one(".author-born-location").string,
        biography=author_soup.select_one(".author-description").string
    )
    return author


def get_author(author_link: str) -> Author:
    """Request and create new Author"""
    author_link = urljoin(BASE_QUOTES_URL, author_link)
    author_page = requests.get(author_link).content
    author_soup = BeautifulSoup(author_page, "html.parser")
    return create_author(author_soup)


@scrape_data
def get_authors_from_page(page_soup: BeautifulSoup) -> [Author]:
    """
        Request new authors that we don't have in cash and update
        authors cash at the end.
    """
    authors_link = page_soup.select(".author ~ a")
    authors_cash = load_authors_cash()

    # request only not cashed/new authors
    unique_authors = {
        author_link["href"] for author_link in authors_link
    }.difference(authors_cash)
    created_authors = [get_author(author_link) for author_link in unique_authors]

    # cash authors links
    authors_cash = authors_cash.union(unique_authors)
    save_authors_cash(authors_cash)

    return created_authors
