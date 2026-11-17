import csv
import time
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"


def get_soup(session: requests.Session, url: str) -> BeautifulSoup:
    response = session.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_quotes(soup: BeautifulSoup) -> list[Quote]:
    quotes = []
    for quote_el in soup.select(".quote"):
        quotes.append(
            Quote(
                text=quote_el.select_one(".text").get_text(strip=True),
                author=quote_el.select_one(".author").get_text(strip=True),
                tags=[
                    tag.get_text(strip=True)
                    for tag in quote_el.select(".tag")
                ],
            )
        )
    return quotes


def next_page_url(soup: BeautifulSoup) -> str | None:
    next_link = soup.select_one("li.next a")
    if next_link is None:
        return None
    return urljoin(BASE_URL, next_link["href"])


def main(output_csv_path: str) -> None:
    session = requests.Session()
    session.headers["User-Agent"] = "py-scrape-quotes/1.0"

    url = BASE_URL
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])

        while url:
            soup = get_soup(session, url)
            for quote in parse_quotes(soup):
                writer.writerow([
                    quote.text,
                    quote.author,
                    ", ".join(quote.tags),
                ])
            url = next_page_url(soup)
            if url:
                time.sleep(1)


if __name__ == "__main__":
    main("quotes.csv")
