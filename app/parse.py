import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[text.text for text in quote.select(".tag")]
    )


def get_all_quotes_from_page(num_of_page: int) -> [Quote]:
    page = requests.get(f"{BASE_URL}/page/{num_of_page}/").content
    soup = BeautifulSoup(page, "html.parser")
    quotes_soup = soup.select(".quote")
    return [get_quote(quote) for quote in quotes_soup]


def qet_quotes_from_all_pages() -> [Quote]:
    num_of_page = 1
    all_quotes = []
    while True:
        page_of_quotes = get_all_quotes_from_page(num_of_page)
        if len(page_of_quotes) == 0:
            break
        all_quotes += page_of_quotes
        num_of_page += 1
    return all_quotes


def main(output_csv_path: str) -> None:
    all_quotes = qet_quotes_from_all_pages()
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(field.name for field in fields(Quote))
        writer.writerows([astuple(quote) for quote in all_quotes])


if __name__ == "__main__":
    main("quotes.csv")
