import csv
import dataclasses
from dataclasses import dataclass, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

HOME_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    birth_date: str
    description: str


QUOTES_FIELDS = [field.name for field in dataclasses.fields(Quote)]
AUTHOR_FIELDS = [field.name for field in dataclasses.fields(Author)]


def parse_author(author: Tag) -> Author:
    return Author(
        name=author.select_one(".author-title").text,
        birth_date=author.select_one(".author-born-date").text,
        description=author.select_one(".author-description").text,
    )


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_single_page_quotes(page: Tag) -> list[Quote]:
    quotes = page.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes(authors_cache: dict[str, Author] | None = None) -> list[Quote]:
    url = HOME_URL
    all_quotes = []
    if authors_cache is None:
        authors_cache = {}
    while url:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        all_quotes.extend(get_single_page_quotes(soup))

        for quote in soup.select(".quote"):
            author_name = quote.select_one(".author").text

            if author_name not in authors_cache:
                author_link = quote.select_one("a[href^='/author/']")["href"]
                author_url = urljoin(url, author_link)
                response = requests.get(author_url, timeout=10)
                response.raise_for_status()
                text = response.content
                author_soup = BeautifulSoup(text, "html.parser")
                author = parse_author(author_soup)
                authors_cache[author_name] = author

        next_page = soup.select_one(".next a")

        if next_page:
            url = urljoin(url, next_page["href"])

        else:
            break
    return all_quotes


def csv_formating(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def author_csv_formating(authors: dict, output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows(astuple(author) for author in authors.values())


def main(output_csv_path: str) -> None:
    authors_cache = {}
    quotes = get_quotes(authors_cache)
    csv_formating(quotes, output_csv_path)
    author_csv_formating(authors_cache, "authors.csv")


if __name__ == "__main__":
    main("quotes.csv")
