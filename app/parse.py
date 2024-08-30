import csv
from dataclasses import dataclass
from typing import Generator

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page(url: str) -> BeautifulSoup:
    page = requests.get(url).content
    return BeautifulSoup(page, "html.parser")


def parse_quote_detail(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_quotes_from_page(soup: BeautifulSoup) -> list[Quote]:
    quotes_soup = soup.select(".quote")
    return [parse_quote_detail(quote_soup) for quote_soup in quotes_soup]


def get_next_page_url(soup: BeautifulSoup) -> str | None:
    next_button = soup.select_one(".next > a")
    if next_button:
        return BASE_URL + next_button["href"]
    return None


def scrape_quotes() -> Generator[Quote, None, None]:
    url = BASE_URL
    while url:
        soup = fetch_page(url)
        quotes = get_quotes_from_page(soup)
        for quote in quotes:
            yield quote
        url = get_next_page_url(soup)


def write_quotes_to_csv(
        quotes: Generator[Quote, None, None], output_csv_path: str
) -> None:
    with open(
            output_csv_path, mode="w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
