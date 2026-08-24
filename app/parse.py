import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    tags_content = quote_soup.select_one(".keywords")["content"]
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=tags_content.split(",") if tags_content else [],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> list[Quote]:
    quotes = []
    url = BASE_URL

    while url:
        page = requests.get(url).content
        page_soup = BeautifulSoup(page, "html.parser")
        quotes.extend(get_single_page_quotes(page_soup))

        next_button = page_soup.select_one(".next a")
        url = BASE_URL + next_button["href"] if next_button else None

    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows(
            [quote.text, quote.author, quote.tags] for quote in quotes
        )


if __name__ == "__main__":
    main("quotes.csv")
