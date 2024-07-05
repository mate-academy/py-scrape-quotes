import csv
import logging
import sys

from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags = [tag.text for tag in quote.select(".tags > .tag")]
    return Quote(text=text, author=author, tags=tags)


def get_single_quotes(page_quote: BeautifulSoup) -> [Quote]:
    quotes = page_quote.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_next_page_url(soup: BeautifulSoup) -> str | None:
    next_page = soup.select_one(".next > a")
    if next_page:
        return BASE_URL + next_page["href"]


def get_quotes() -> [Quote]:
    quotes = []
    page_url = BASE_URL
    while page_url:
        logging.info(f"Getting page {page_url}")
        page = requests.get(page_url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(get_single_quotes(soup))
        page_url = get_next_page_url(soup)
    return quotes


def save_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    save_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
