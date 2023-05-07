import csv
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup
import requests

WEBSITE_URL = "http://quotes.toscrape.com"
TOTAL_PAGES = 10


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    @classmethod
    def class_keys(cls) -> Any:
        return cls.__annotations__.keys()


def scrape_quotes_from_page(page_url: str) -> list[Quote]:
    quotes = []
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")
    for quote in soup.find_all("div", class_="quote"):
        text = quote.find("span", class_="text").text
        author = quote.find("small", class_="author").text
        tags = [tag.text for tag in quote.find_all("a", class_="tag")]
        quotes.append(Quote(text, author, tags))
    return quotes


def scrape_quotes() -> list[Quote]:
    quotes = []
    for page_number in range(1, TOTAL_PAGES + 1):
        print(f"Scraping page {page_number}...")
        page_url = f"{WEBSITE_URL}/page/{page_number}"
        quotes.extend(scrape_quotes_from_page(page_url))
    return quotes


def save_quotes(output_csv_path: str, quotes: list) -> None:
    with open(output_csv_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(Quote.class_keys())
        writer.writerows(
            [(quote.text, quote.author, quote.tags) for quote in quotes]
        )


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    save_quotes(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
