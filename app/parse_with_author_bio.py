import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"

session = requests.Session()


@dataclass
class Author:
    name: str
    birth_date: str
    bio: str


AUTHOR_FIELDS = [field.name for field in fields(Author)]


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]
    author_data: Author


QUOTE_FIELDS_WITHOUT_AUTHOR_DATA = [field.name for field in fields(Quote)][:-1]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ],
)


def get_page_soup(url: str) -> BeautifulSoup:
    response = session.get(url)
    return BeautifulSoup(response.text, "html.parser")


def parse_author_bio_from_page(page_soup: BeautifulSoup) -> Author:
    name = page_soup.select_one("h3.author-title").text
    birth_date = page_soup.select_one("span.author-born-date").text
    bio = page_soup.select_one("div.author-description").text.lstrip()

    return Author(name=name, birth_date=birth_date, bio=bio)


author_cache: dict[str, Author] = {}


def get_author(url: str) -> Author:
    if url in author_cache:
        logging.debug(f"Author from cache: {url}")
        return author_cache[url]

    logging.info(f"Fetching author bio: {url}")
    soup = get_page_soup(url)
    author = parse_author_bio_from_page(soup)
    author_cache[url] = author
    return author


def parse_one_quote(quote: Tag) -> Quote:
    text = quote.select_one("span.text").text

    tags_container = quote.select_one("div.tags")
    tags = [
        tag.text
        for tag in tags_container.find_all("a", class_="tag")
    ]

    author_bio_url = quote.find("a", string="(about)").get("href")
    author_bio_url = urljoin(BASE_URL, author_bio_url)
    author = get_author(author_bio_url)

    return Quote(text=text, author=author.name, tags=tags, author_data=author)


def get_next_page_soup(page_soup: BeautifulSoup) -> BeautifulSoup | None:
    next_li = page_soup.find("li", class_="next")
    next_a = next_li.select_one("a") if next_li else None
    next_href = next_a.get("href") if next_a else None

    if next_href:
        next_url = urljoin(BASE_URL, next_href)
        return get_page_soup(next_url)
    return None


def get_quotes_from_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select("div.quote")
    return [parse_one_quote(quote) for quote in quotes]


def get_all_pages_quotes() -> list[Quote]:
    # Main Page
    logging.info("Parse first page...")
    page_soup = get_page_soup(BASE_URL)
    all_quotes = get_quotes_from_page(page_soup)
    # Next page
    next_page_soup = get_next_page_soup(page_soup)
    while next_page_soup:
        logging.info("Parse next page...")
        all_quotes.extend(get_quotes_from_page(next_page_soup))
        next_page_soup = get_next_page_soup(next_page_soup)

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    rows = []
    for quote in quotes:
        # Get tuple without author_data ("text", "author", "tags")
        tuple_quote = astuple(quote)[:-1]
        # Tags list from list to str
        tags_list = tuple_quote[-1]
        fixed = tuple_quote[:-1] + (", ".join(tags_list),)
        rows.append(fixed)

    with open(output_csv_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS_WITHOUT_AUTHOR_DATA)
        writer.writerows(rows)
    logging.info("Quotes written to csv...!")


def write_author_to_csvs(quotes: list[Quote]) -> None:
    authors = []
    for quote in quotes:
        authors.append(astuple(quote.author_data))
    with open("authors_bio.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows(authors)
    logging.info("Authors written to csv...!")


def main(output_csv_path: str) -> None:
    quotes_list = get_all_pages_quotes()
    write_quotes_to_csv(quotes_list, output_csv_path)
    write_author_to_csvs(quotes_list)


if __name__ == "__main__":
    main("quotes.csv")
