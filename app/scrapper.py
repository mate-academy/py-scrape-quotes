import logging
from urllib.parse import urljoin

import requests
from bs4 import ResultSet, Tag, BeautifulSoup

from app.config import URL, Author
from app.parser import parse_single_author
from logger import configure_logger


configure_logger()


def scrape_one_page(url: str) -> (ResultSet[Tag], str | None):
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    quotes = soup.select(".quote")

    next_page = soup.select_one(".next > a")
    if next_page:
        next_page_url = urljoin(url, next_page["href"])
    else:
        next_page_url = None

    return quotes, next_page_url


def scrape_all_raw_quotes(url: str) -> list[Tag]:
    all_raw_quotes = []
    current_url = url
    current_page = 1

    while current_url:
        logging.info(f"Scraping page {current_page}")
        quotes, current_url = scrape_one_page(current_url)
        all_raw_quotes.extend(quotes)
        current_page += 1

    return all_raw_quotes


def get_unique_authors_urls(raw_quotes: list[Tag]) -> set[str]:
    authors_urls = set()

    for quote in raw_quotes:
        author_page = quote.select_one("a[href*='/author/']")
        if author_page:
            author_page_url = urljoin(URL, author_page["href"])
            authors_urls.add(author_page_url)

    return authors_urls


def scrape_and_parse_all_authors(raw_quotes: list[Tag]) -> list[Author]:
    authors_urls = get_unique_authors_urls(raw_quotes)
    authors = []
    for i, url in enumerate(authors_urls, 1):
        try:
            logging.info(f"Scraping author {i}")
            page = requests.get(url).content
            soup = BeautifulSoup(page, "html.parser")
            author = parse_single_author(soup)
            authors.append(author)
        except Exception as e:
            logging.error(f"Failed to scrape {url}: {e}")

    return authors
