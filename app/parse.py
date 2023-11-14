import csv
from dataclasses import dataclass
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    tags = []
    for tag in quote_soup.select(".tag"):
        tags.append(tag.text)
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=tags
    )


def get_home_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> List[Quote]:
    all_quotes = []
    global BASE_URL
    while True:
        page = requests.get(BASE_URL).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = get_home_quotes(soup)
        all_quotes.extend(quotes)
        next_page = soup.select_one("li.next a")
        if next_page is None:
            break
        BASE_URL = urljoin(BASE_URL, next_page["href"])

    return all_quotes


def write_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("text", "author", "tags"))
        for quoter in quotes:
            writer.writerow((quoter.text, quoter.author, quoter.tags))


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
