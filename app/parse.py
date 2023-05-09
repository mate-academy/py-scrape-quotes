import csv
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [get_single_quote(single_quote) for single_quote in quotes]


def get_quotes() -> List[Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(soup)

    for page_num in range(2, 11):
        page = requests.get(BASE_URL + f"/page/{page_num}")
        soup = BeautifulSoup(page.content, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))

    return all_quotes


def write_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
