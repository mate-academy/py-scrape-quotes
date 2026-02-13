import csv
from dataclasses import dataclass, fields, astuple
from typing import Generator, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/page/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def page_generator() -> Generator[BeautifulSoup, None, None]:
    page = 1

    while True:
        url = urljoin(BASE_URL, f"{page}/")
        response = requests.get(url)
        if "No quotes found!" in response.text:
            break
        soup = BeautifulSoup(response.content, "html.parser")
        yield soup
        page += 1


def parse_page(soup: BeautifulSoup) -> List[Quote]:
    quotes = []

    for quote in soup.select("div.quote"):
        text = quote.select_one("span.text").get_text(strip=True)
        author = quote.select_one("small.author").get_text(strip=True)
        tags = [t.get_text(strip=True) for t in quote.select("div.tags a.tag")]

        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def get_all_quotes() -> List[Quote]:
    all_quotes = []

    for soup in page_generator():
        all_quotes.extend(parse_page(soup))

    return all_quotes


def write_quotes_to_csv(quotes: List[Quote], path: str) -> None:
    with open(path, "w", ) as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
