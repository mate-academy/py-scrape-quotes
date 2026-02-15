import csv
from dataclasses import dataclass, fields, astuple
from typing import Generator

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]



BASE_URL = "https://quotes.toscrape.com/page/"


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


def parse_page(soup: BeautifulSoup) -> list[Quote]:
    quotes = []

    for quote in soup.select("div.quote"):
        text = quote.select_one("span.text").get_text(strip=True)
        author = quote.select_one("small.author").get_text(strip=True)
        tags = [t.get_text(strip=True) for t in quote.select("div.tags a.tag")]

        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def main(output_csv_path: str) -> None:
    all_quotes = []

    for soup in page_generator():
        all_quotes.extend(parse_page(soup))



    with open(output_csv_path, "w", ) as f:
        writer = csv.writer(f)
        writer.writerow([field.name for field in fields(Quote)])
        writer.writerows(astuple(quote) for quote in all_quotes)


if __name__ == "__main__":
    main("quotes.csv")
