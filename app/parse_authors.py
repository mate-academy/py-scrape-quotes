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


@dataclass
class AuthorParser:
    # page_soup response page from BASE_QUOTES_URL
    page_soup: BeautifulSoup

    @classmethod
    def load_authors_cash(cls) -> set:
        try:
            with open(AUTHOR_CASH_FILE, "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return set()

    @classmethod
    def save_authors_cash(cls, author_cash: set) -> None:
        with open(AUTHOR_CASH_FILE, "wb") as file:
            pickle.dump(author_cash, file)

    def create_author(self, author_soup: BeautifulSoup) -> Author:
        return Author(
            full_name=author_soup.select_one(".author-title").string,
            born_date=author_soup.select_one(".author-born-date").string,
            born_location=author_soup.select_one(
                ".author-born-location"
            ).string,
            biography=author_soup.select_one(".author-description").string
        )

    def get_author(self, author_link: str) -> BeautifulSoup:
        """Request author detail BeautifulSoup page"""
        author_link = urljoin(BASE_QUOTES_URL, author_link)
        author_page = requests.get(author_link).content
        author_soup = BeautifulSoup(author_page, "html.parser")
        return author_soup

    def get_authors_link(self) -> set[str]:
        """Return set of author detail URL"""
        authors_link = self.page_soup.select(".author ~ a")
        return {author_link["href"] for author_link in authors_link}

    def get_not_cashed_authors_link(self) -> set[str]:
        """Return set of author links which are not in cash"""
        authors_link = self.get_authors_link()
        authors_cash = AuthorParser.load_authors_cash()

        unique_authors = authors_link.difference(authors_cash)
        authors_cash = authors_cash.union(unique_authors)

        AuthorParser.save_authors_cash(authors_cash)

        return unique_authors


@scrape_data
def get_authors_from_page(page_soup: BeautifulSoup) -> [Author]:
    parser = AuthorParser(page_soup)
    unique_authors = parser.get_not_cashed_authors_link()

    created_authors = [
        parser.create_author(
            parser.get_author(author_link)
        )
        for author_link in unique_authors
    ]

    return created_authors
