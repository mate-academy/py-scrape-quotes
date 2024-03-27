from typing import Callable
from bs4 import BeautifulSoup


BASE_QUOTES_URL = "https://quotes.toscrape.com/"


def scrape_data(func: Callable) -> Callable:
    """
        Decorator for keeping data from scrapping since
        we don't want a lot of duplication in main function
    """
    scraped_data = []

    def wrapper(parser_soup: BeautifulSoup):
        scraped_data.extend(func(parser_soup))
        return scraped_data
    return wrapper
