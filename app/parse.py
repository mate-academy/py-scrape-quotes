import csv
from dataclasses import astuple, dataclass, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_soup(url: str, session: requests.Session) -> BeautifulSoup:
    response = session.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_all_quotes() -> list[Quote]:
    quotes = []

    with requests.Session() as session:
        url = BASE_URL

        while url:
            soup = get_soup(url, session)
            quotes.extend(
                parse_single_quote(quote_soup)
                for quote_soup in soup.select(".quote")
            )

            next_button = soup.select_one(".next a")
            url = urljoin(url, next_button["href"]) if next_button else None

    return quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


# ---- Optional task: authors' biography, with per-author caching ----


@dataclass
class Author:
    name: str
    born_date: str
    born_location: str
    description: str


AUTHOR_FIELDS = [field.name for field in fields(Author)]


def get_all_quotes_and_authors() -> tuple[list[Quote], list[Author]]:
    quotes = []
    # author url -> Author, avoids re-fetching the same author page
    authors_cache: dict[str, Author] = {}

    with requests.Session() as session:
        url = BASE_URL

        while url:
            soup = get_soup(url, session)

            for quote_soup in soup.select(".quote"):
                quotes.append(parse_single_quote(quote_soup))

                about_link = quote_soup.select_one(".author + a")
                author_url = urljoin(url, about_link["href"])
                if author_url not in authors_cache:
                    author_soup = get_soup(author_url, session)
                    authors_cache[author_url] = parse_single_author(
                        author_soup
                    )

            next_button = soup.select_one(".next a")
            url = urljoin(url, next_button["href"]) if next_button else None

    return quotes, list(authors_cache.values())


def parse_single_author(author_soup: BeautifulSoup) -> Author:
    return Author(
        name=author_soup.select_one(".author-title").text,
        born_date=author_soup.select_one(".author-born-date").text,
        born_location=author_soup.select_one(".author-born-location").text,
        description=author_soup.select_one(".author-description").text.strip(),
    )


def write_authors_to_csv(authors: list[Author], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows(astuple(author) for author in authors)


def main_with_authors(quotes_csv_path: str, authors_csv_path: str) -> None:
    quotes, authors = get_all_quotes_and_authors()
    write_quotes_to_csv(quotes, quotes_csv_path)
    write_authors_to_csv(authors, authors_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
