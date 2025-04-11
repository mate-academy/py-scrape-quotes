import csv
import dataclasses
from dataclasses import dataclass
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
import requests


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


@dataclass
class Author:
    name: str
    born_date: str
    born_place: str


TAGS_FIELDS = [field.name for field in dataclasses.fields(Quote)]

author_cache = {}


def parse_authors(author_url: str) -> Author:
    response = requests.get(author_url)
    soup = BeautifulSoup(response.text, "html.parser")

    name = soup.select_one("h3.author-title").text.strip()
    born_date = soup.select_one(".author-born-date").text.strip()
    born_place = soup.select_one(".author-born-location").text.strip()

    return Author(
        name=name,
        born_date=born_date,
        born_place=born_place,
    )


def parse_single_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").text.strip()
    author_name = quote.select_one(".author").text.strip()
    tags = [tag.text for tag in quote.select(".tags .tag")]

    author_relative_url = quote.select_one("a")["href"]
    author_url = urljoin(BASE_URL, author_relative_url)

    if author_name not in author_cache:
        author_cache[author_name] = parse_authors(author_url)

    return Quote(
        text=text,
        author=author_name,
        tags=tags
    )


def get_quotes() -> [Quote]:
    text = requests.get(BASE_URL)
    soup = BeautifulSoup(text.content, "html.parser")
    quotes_tag = soup.select("div.quote")
    return [parse_single_quote(tag) for tag in quotes_tag]


def get_next_page_url(page_soup: BeautifulSoup, current_url: str) -> str | None:
    next_btn = page_soup.select_one("li.next a")
    if next_btn:
        relative_url = next_btn["href"]
        return urljoin(current_url, relative_url)
    return None


def get_all_quotes() -> [Quote]:
    quotes = []
    url = BASE_URL
    while url:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        quote_tags = soup.select("div.quote")
        quotes.extend([parse_single_quote(q) for q in quote_tags])
        url = get_next_page_url(soup, url)
    return quotes


def write_authors_to_csv(authors: dict[str, Author], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "born_date", "born_place"])
        for author in authors.values():
            writer.writerow([author.name, author.born_date, author.born_place])


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(TAGS_FIELDS)
        writer.writerows([dataclasses.astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)
    write_authors_to_csv(author_cache, "authors.csv")


if __name__ == "__main__":
    main("quotes.csv")
