import csv
import time
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

MAIN_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    born_date: str
    born_location: str
    description: str


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHORS_FIELDS = [field.name for field in fields(Author)]

# author caching
author_cache: dict[str, Author] = {}


def parse_single_quote(quote: Tag) -> Quote:
    author_name = quote.select_one("small.author").text.strip()
    tags = [tag.text for tag in quote.select(".tag")]
    return Quote(
        text=quote.select_one("span.text").text.strip(),
        author=author_name,
        tags=tags
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select("div.quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_author_info(author_url: str) -> Author:
    if author_url in author_cache:
        return author_cache[author_url]

    response = requests.get(author_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    author = Author(
        name=soup.select_one("h3.author-title").text.strip(),
        born_date=soup.select_one(".author-born-date").text.strip(),
        born_location=soup.select_one(".author-born-location").text.strip(),
        description=soup.select_one(".author-description").text.strip(),
    )

    author_cache[author_url] = author
    time.sleep(0.3)  # be gentle
    return author


def get_page_quotes() -> list[Quote]:
    all_quotes = []
    next_url = MAIN_URL

    while next_url:
        response = requests.get(next_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        all_quotes.extend(get_single_page_quotes(soup))

        next_button = soup.select_one("li.next a")
        if next_button:
            next_url = urljoin(MAIN_URL, next_button["href"])
            time.sleep(0.5)
        else:
            next_url = None

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_authors_to_csv(authors: list[Author], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(AUTHORS_FIELDS)
        writer.writerows([astuple(author) for author in authors])


def main(output_csv_path: str) -> None:
    quotes = get_page_quotes()

    for quote in quotes:
        author_url = urljoin(
            MAIN_URL, f'author/{quote.author.replace(" ", "-")}'
        )
        get_author_info(author_url)

    authors = list(author_cache.values())

    write_quotes_to_csv(quotes, output_csv_path)
    write_authors_to_csv(authors, "authors.csv")


if __name__ == "__main__":
    main("quotes.csv")
