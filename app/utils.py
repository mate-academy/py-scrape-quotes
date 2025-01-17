import csv
import logging
from dataclasses import astuple, fields
from urllib.parse import urljoin

from bs4 import Tag

from app.models import Author, Quote


BASE_URL = "https://quotes.toscrape.com/"
QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


def parse_single_quote(quote_div: Tag) -> Quote:
    """Parse a single quote from the quote div element."""
    return Quote(
        text=quote_div.select_one(".text").text,
        author=quote_div.select_one(".author").text,
        tags=[tag.text for tag in quote_div.select(".tag")],
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    """Extract all quotes from a single page."""
    quotes_divs = page_soup.select(".quote")
    return [parse_single_quote(quote_div) for quote_div in quotes_divs]


def get_next_page_url(page_soup: Tag) -> str | None:
    """Get URL of the next page if it exists."""
    next_button = page_soup.select_one("li.next a")

    if next_button:
        return urljoin(BASE_URL, next_button["href"])

    return None


def get_author_url(quote_div: Tag) -> str:
    """Get author page URL from the quote div element."""
    about_link = quote_div.select_one(".author + a")
    return urljoin(BASE_URL, about_link["href"])


def parse_author_bio(page_soup: Tag) -> Author:
    """Parse author biography from the author's page."""
    born_date = page_soup.select_one(".author-born-date").text
    born_location = page_soup.select_one(".author-born-location").text
    description = page_soup.select_one(".author-description").text.strip()
    name = page_soup.select_one(".author-title").text

    return Author(name, born_date, born_location, description)


def write_quotes_to_csv(quotes: list[Quote], output_path: str) -> None:
    """Write quotes to a CSV file."""
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])

    logging.info(f"Quotes have been saved to {output_path}")


def write_authors_to_csv(authors: list[Author], output_path: str) -> None:
    """Write authors to a CSV file."""
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows([astuple(author) for author in authors])

    logging.info(f"Authors have been saved to {output_path}")
