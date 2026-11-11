import csv
from dataclasses import dataclass, fields, astuple
from typing import Generator
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def fetch_page_content(url: str) -> bytes | None:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        if not soup.select(".quote"):
            return None
        return response.content
    except requests.RequestException:
        return None


def get_pages() -> Generator[bytes, None, None]:
    """Generator that yields page content(bytes) for each page."""
    page_number = 1
    while True:
        url = urljoin(BASE_URL, f"/page/{page_number}/")
        content = fetch_page_content(url)
        if not content:
            break
        yield content
        page_number += 1


def parse_page(page: bytes) -> list[Quote]:
    soup = BeautifulSoup(page, "lxml")
    quotes: list[Quote] = []

    for quote in soup.select("div.quote"):
        text = quote.select_one("span.text")
        author = quote.select_one("small.author")
        tags = [tag.text for tag in quote.select("a.tag")]

        quotes.append(Quote(text.text, author.text, tags))
    return quotes


def parse_all_pages() -> list[Quote]:
    quotes: list[Quote] = []
    for page in get_pages():
        quotes.extend(parse_page(page))
    return quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(parse_all_pages(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
