import time
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin
import csv

import requests
from bs4 import BeautifulSoup, Tag


HOME_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").get_text(strip=True)
    author = quote.select_one(".author").get_text(strip=True)
    tags = [t.get_text(strip=True) for t in quote.select(".tag")]
    return Quote(text=text, author=author, tags=tags)


def get_quotes() -> list[Quote]:
    text = requests.get(HOME_URL).content
    soup = BeautifulSoup(text, "html.parser")
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> list[Quote]:
    url = HOME_URL
    all_quotes = []
    while url:
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        page_quotes = [parse_single_quote(q) for q in soup.select(".quote")]
        all_quotes.extend(page_quotes)
        next_link = soup.select_one(".pager .next a")
        url = urljoin(HOME_URL, next_link['href']) if next_link else None
        time.sleep(0.2)
    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    with open(output_csv_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_FIELDS)
        for q in quotes:
            writer.writerow([q.text, q.author, ";".join(q.tags)])


if __name__ == "__main__":
    main("quotes.csv")
