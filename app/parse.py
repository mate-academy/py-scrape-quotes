import csv
from dataclasses import dataclass, astuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags .tag")],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    page_url = BASE_URL

    while True:
        page = requests.get(page_url).content
        page_soup = BeautifulSoup(page, "html.parser")

        all_quotes.extend(get_single_page_quotes(page_soup))

        next_button = page_soup.select_one(".next a")
        if next_button is None:
            break

        page_url = BASE_URL + next_button["href"].lstrip("/")

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
