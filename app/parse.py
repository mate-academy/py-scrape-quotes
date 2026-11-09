import csv
from dataclasses import astuple, dataclass, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Author:
    name: str
    born_date: str
    born_location: str
    biography: str


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one("span.text").text,
        author=quote.select_one("small.author").text,
        tags=[tag.text for tag in quote.select("a.tag")],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select("div.quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    url = BASE_URL

    while url:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        next_link = soup.select_one("li.next a")
        url = urljoin(BASE_URL, next_link["href"]) if next_link else None
    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_all_quotes(), output_csv_path)


def get_author_urls() -> dict[str, str]:
    author_urls = {}
    url = BASE_URL

    while url:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        for quote in soup.select("div.quote"):
            name = quote.select_one("small.author").text
            if name not in author_urls:
                author_urls[name] = urljoin(
                    BASE_URL, quote.select_one("span a")["href"]
                )
        next_link = soup.select_one("li.next a")
        url = urljoin(BASE_URL, next_link["href"]) if next_link else None
    return author_urls


def parse_single_author(author_soup: BeautifulSoup) -> Author:
    return Author(
        name=author_soup.select_one("h3.author-title").text.strip(),
        born_date=author_soup.select_one("span.author-born-date").text,
        born_location=author_soup.select_one("span.author-born-location").text,
        biography=author_soup.select_one(
            "div.author-description"
        ).text.strip(),
    )


def get_all_authors() -> list[Author]:
    return [
        parse_single_author(BeautifulSoup(
            requests.get(url).content, "html.parser")
        )
        for url in get_author_urls().values()
    ]


def write_authors_to_csv(authors: list[Author], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows([astuple(author) for author in authors])


def main_authors(output_csv_path: str) -> None:
    write_authors_to_csv(get_all_authors(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
    main_authors("authors.csv")
