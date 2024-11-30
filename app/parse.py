from typing import List

import requests
from bs4 import BeautifulSoup, Tag
import csv
from dataclasses import dataclass, astuple

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


def parse_single_quote(soup: Tag) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=[tag.text for tag in soup.select("a.tag")],
    )


def get_quotes_from_page(url: str) -> [Quote]:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    quotes = [parse_single_quote(quote) for quote in soup.select(".quote")]

    next_button = soup.select_one(".next > a")
    next_page_url = f"{BASE_URL}{next_button['href']}" if next_button else None

    return quotes, next_page_url


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    current_url = BASE_URL

    while current_url:
        quotes, next_page_url = get_quotes_from_page(current_url)
        all_quotes.extend(quotes)
        current_url = next_page_url

    return all_quotes


def save_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> [Quote]:
    quotes = get_all_quotes()
    save_quotes_to_csv(quotes, output_csv_path)
    print(f"Saved {len(quotes)} quotes to {output_csv_path}")


if __name__ == "__main__":
    main("quotes.csv")
