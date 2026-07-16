import csv
import time
from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_page(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_quotes(soup: BeautifulSoup) -> list[Quote]:
    quotes = []
    for quote_div in soup.select(".quote"):
        text = quote_div.select_one(".text").get_text()
        author = quote_div.select_one(".author").get_text()
        tags = [tag.get_text() for tag in quote_div.select(".tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))
    return quotes


def get_next_page_url(soup: BeautifulSoup) -> Optional[str]:
    next_btn = soup.select_one(".next a")
    if next_btn:
        return BASE_URL + next_btn["href"]
    return None


def main(output_csv_path: str) -> None:
    all_quotes = []
    url: Optional[str] = BASE_URL

    while url:
        soup = get_page(url)
        all_quotes.extend(parse_quotes(soup))
        url = get_next_page_url(soup)
        if url:
            time.sleep(1)

    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in all_quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


if __name__ == "__main__":
    main("quotes.csv")
