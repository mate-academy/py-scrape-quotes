import dataclasses
from typing import List

import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://quotes.toscrape.com/page/{}/"


@dataclasses.dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in dataclasses.fields(Quote)]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    text_element = quote.select_one(".text")
    author_element = quote.select_one(".author")
    tag_elements = quote.select(".tag")

    text = text_element.get_text(strip=True) if text_element else ""
    author = author_element.get_text(strip=True) if author_element else ""
    tags = [
        tag.get_text(strip=True)
        for tag in tag_elements]\
        if tag_elements else []

    return Quote(text=text, author=author, tags=tags)


def get_quotes_data() -> List[Quote]:
    page_number = 1
    quotes = []

    while True:
        url = BASE_URL.format(page_number)
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error fetching page {page_number}."
                  f"Status code: {response.status_code}")
            break

        page_soup = BeautifulSoup(response.content, "html.parser")
        quotes_on_page = page_soup.select(".quote")
        quotes.extend([parse_single_quote(quote) for quote in quotes_on_page])

        next_button = page_soup.select_one(".pager .next a")
        if not next_button:
            break

        page_number += 1

    return quotes


def write_to_csv(path: str, quotes: List[Quote]) -> None:
    with open(path, "w", encoding="utf8", newline="") as f:
        writer = csv.writer(f)
        print(type(quotes[0]))
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([dataclasses.astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes_data()
    write_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
