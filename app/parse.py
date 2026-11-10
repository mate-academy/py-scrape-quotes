import csv
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = [tag.text for tag in quote_soup.select(".tag")]

    return Quote(text=text, author=author, tags=tags)


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_page_soup(page_number: int) -> BeautifulSoup:
    response = requests.get(f"{BASE_URL}page/{page_number}/")
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    page_number = 1
    while True:
        page_soup = get_page_soup(page_number)
        page_quotes = get_single_page_quotes(page_soup)
        if not page_quotes:
            break
        all_quotes.extend(page_quotes)
        page_number += 1
    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")