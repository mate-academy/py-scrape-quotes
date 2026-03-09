import time
from dataclasses import dataclass, fields, astuple
import csv

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    biography: str


AUTHOR_FIELDS = [field.name for field in fields(Author)]
QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_soup(url: str) -> BeautifulSoup:
    return BeautifulSoup(requests.get(url).text, "html.parser")


def scrape_quote(element: Tag) -> Quote:
    return Quote(
        text=element.select_one(".text").text,
        author=element.select_one(".author").text,
        tags=[tag.get_text(strip=True) for tag in element.select(".tag")],
    )


def scrape_author(author_url: str) -> Author:
    author_soup = get_soup(BASE_URL + author_url)
    return Author(
        name=author_soup.select_one(".author-title").text,
        biography=author_soup.select_one(".author-description").text,
    )


def parse_quote() -> tuple[list[Quote], dict[str, Author]]:
    all_quotes = []
    authors_cache = {}
    page = 1

    while True:
        url = f"{BASE_URL}page/{page}/"
        soup = get_soup(url)

        for element in soup.select(".quote"):
            all_quotes.append(scrape_quote(element))

            author_url = element.select_one("a")["href"]
            if author_url not in authors_cache:
                authors_cache[author_url] = scrape_author(author_url)

        next_page = soup.select_one("li.next")
        if not next_page:
            break
        page += 1
        time.sleep(1)

    return all_quotes, authors_cache


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_authors_to_csv(authors: list[Author], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows([astuple(author) for author in authors])


def main(output_csv_path: str) -> None:
    all_quotes, authors_cache = parse_quote()
    write_quotes_to_csv(all_quotes, output_csv_path)
    write_authors_to_csv(list(authors_cache.values()), "authors.csv")


if __name__ == "__main__":
    main("quotes.csv")
