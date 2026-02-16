import csv
import time
from dataclasses import dataclass, fields
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
TIMEOUT = 10
DELAY_SECONDS = 1


def page_generator() -> Generator[BeautifulSoup, None, None]:
    page = 1

    while True:
        url = urljoin(BASE_URL, f"{page}/")

        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"Request failed for {url}: {exc}")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        quote_blocks = soup.select("div.quote")
        if not quote_blocks:
            break

        yield soup
        page += 1
        time.sleep(DELAY_SECONDS)


def parse_page(soup: BeautifulSoup) -> list[Quote]:
    quotes: list[Quote] = []

    for quote in soup.select("div.quote"):
        text_el = quote.select_one("span.text")
        author_el = quote.select_one("small.author")

        if text_el is None or author_el is None:
            continue

        text = text_el.get_text(strip=True)
        author = author_el.get_text(strip=True)
        tags = [t.get_text(strip=True) for t in quote.select("div.tags a.tag")]

        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def main(output_csv_path: str) -> None:
    all_quotes: list[Quote] = []
    for soup in page_generator():
        all_quotes.extend(parse_page(soup))

    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([field.name for field in fields(Quote)])

        for quote in all_quotes:
            tags_str = str(quote.tags)
            writer.writerow([quote.text, quote.author, tags_str])


if __name__ == "__main__":
    main("quotes.csv")
