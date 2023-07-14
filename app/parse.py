import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"
OUTPUT_CSV_PATH = "result.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.find_all("a", class_="tag")]
    )


def get_all_products_from_single_page(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_list_quotes() -> [Quote]:
    quotes = []
    page = 1
    while True:
        url = f"{BASE_URL}/page/{page}/"
        parsed_page = requests.get(url).content
        page_soup = BeautifulSoup(parsed_page, "html.parser")
        parsed_quotes = get_all_products_from_single_page(page_soup)
        if not parsed_quotes:
            break
        quotes.extend(parsed_quotes)
        page += 1

    return quotes


def main(output_csv_path: str) -> None:
    get_list_quotes()
    quotes = get_list_quotes()
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("result.csv")
