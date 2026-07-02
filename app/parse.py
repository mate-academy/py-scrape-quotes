import csv
from dataclasses import dataclass
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


BASE_URL = "https://quotes.toscrape.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_page_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()

    return response.text


def parse_quote(quote_tag: Tag) -> Quote:
    text = quote_tag.select_one(".text")
    author = quote_tag.select_one(".author")
    tags = quote_tag.select(".tag")

    return Quote(
        text=text.get_text(strip=True) if text else "",
        author=author.get_text(strip=True) if author else "",
        tags=[tag.get_text(strip=True) for tag in tags],
    )


def parse_quotes(html: str) -> tuple[list[Quote], str | None]:
    soup = BeautifulSoup(html, "html.parser")
    quotes = [parse_quote(quote) for quote in soup.select(".quote")]
    next_page = soup.select_one("li.next a")

    return quotes, next_page["href"] if next_page else None


def get_all_quotes() -> list[Quote]:
    url = BASE_URL
    quotes = []

    while url:
        html = get_page_html(url)
        page_quotes, next_page = parse_quotes(html)
        quotes.extend(page_quotes)
        url = urljoin(url, next_page) if next_page else None

        if url:
            sleep(0.1)

    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows(
            [quote.text, quote.author, quote.tags]
            for quote in quotes
        )


if __name__ == "__main__":
    main("quotes.csv")
