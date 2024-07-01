import csv
from dataclasses import dataclass, fields, asdict
from datetime import date, datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    bio: str
    born_date: date
    born_location: str


def write_csv(output_csv_path: str, data_list: list, headers: list) -> None:
    with open(output_csv_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, headers)
        writer.writeheader()
        for obj in data_list:
            writer.writerow(asdict(obj))


def parse_quote(soups: BeautifulSoup) -> list[Quote]:
    return [
        Quote(
            text=quote.select_one(".text").text,
            author=quote.select_one(".author").text,
            tags=[tag.text for tag in quote.select(".tag")]
        )
        for quote in soups.select(".quote")
    ]


def parse_authors_href(soups: BeautifulSoup) -> set:
    return {
        author_span.select_one("a")["href"]
        for author_span in soups.select("span:has(small.author)")
    }


def parse_all_author(authors_href: set) -> list[Author]:
    all_authors = []
    for href in authors_href:
        response = requests.get(urljoin(BASE_URL, href))
        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        author_details = soup.select_one(".author-details")
        all_authors.append(Author(
            name=author_details.select_one(".author-title").text,
            bio=author_details.select_one(".author-description").text,
            born_location=author_details.select_one(
                ".author-born-location"
            ).text,
            born_date=datetime.strptime(
                author_details.select_one(".author-born-date").text,
                "%B %d, %Y"
            )
        ))
    return all_authors


def parse_page(url: str) -> tuple[list[Quote], set] | None:
    response = requests.get(url)
    if response.status_code != 200:
        return None

    soups = BeautifulSoup(response.text, "html.parser")
    if soups.select_one(".quote"):
        return parse_quote(soups), parse_authors_href(soups)


def main(
        quote_csv_path: str = "quotes.csv",
        author_csv_path: str = "authors.csv"
) -> None:
    page = 1
    all_quotes = []
    unique_authors = set()
    quotes_fields = [field.name for field in fields(Quote)]
    author_fields = [field.name for field in fields(Author)]
    while response := parse_page(
            urljoin(BASE_URL, f"/page/{page}/")
    ):
        quote, authors_href = response
        all_quotes.extend(quote)
        unique_authors.update(authors_href)
        page += 1

    all_author = parse_all_author(unique_authors)
    write_csv(quote_csv_path, all_quotes, quotes_fields)
    write_csv(author_csv_path, all_author, author_fields)


if __name__ == "__main__":
    main("quotes.csv")
