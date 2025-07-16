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
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ],
)


def parse_one_quote(quote: Tag) -> Quote:
    text = quote.select_one("span.text").text
    author = quote.select_one("small.author").text

    tags_container = quote.select_one("div.tags")
    tags = [
        tag.text
        for tag in tags_container.find_all("a", class_="tag")
    ]

    return Quote(text=text, author=author, tags=tags)


def get_page_soup(url: str) -> BeautifulSoup:
    response = session.get(url)
    return BeautifulSoup(response.text, "html.parser")


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
        tuple_quote = astuple(quote)
        # Tags list from list to str
        tags_list = tuple_quote[-1]
        fixed = tuple_quote[:-1] + (", ".join(tags_list),)
        rows.append(fixed)

    with open(output_csv_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(rows)


def main(output_csv_path: str) -> None:
    quotes_list = get_all_pages_quotes()
    write_quotes_to_csv(quotes_list, output_csv_path)
    logging.info("Parsed all quotes...!")


if __name__ == "__main__":
    main("quotes.csv")
