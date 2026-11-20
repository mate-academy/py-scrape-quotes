import csv
import time
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
REQUEST_DELAY = 0.2


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page(url: str) -> str:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def parse_quotes(html: str) -> list[Quote]:
    soup = BeautifulSoup(html, "html.parser")
    quotes: list[Quote] = []

    for quote_div in soup.select("div.quote"):
        text_el = quote_div.select_one("span.text")
        author_el = quote_div.select_one("small.author")
        if text_el is None or author_el is None:
            continue
        tags = [
            tag.get_text() for tag in quote_div.select("div.tags a.tag")
        ]
        quotes.append(Quote(
            text=text_el.get_text(),
            author=author_el.get_text(),
            tags=tags,
        ))

    return quotes


def get_next_page(html: str, current_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")
    if next_link is None:
        return None
    href = next_link.get("href")
    if not href:
        return None
    return urljoin(current_url, href)


def scrape_quotes(start_url: str = BASE_URL) -> list[Quote]:
    all_quotes: list[Quote] = []
    url: str | None = start_url

    while url is not None:
        html = fetch_page(url)
        all_quotes.extend(parse_quotes(html))
        next_url = get_next_page(html, url)
        if next_url is not None:
            time.sleep(REQUEST_DELAY)
        url = next_url

    return all_quotes


def save_quotes(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    save_quotes(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
