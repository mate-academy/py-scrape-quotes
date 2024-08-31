import csv
from dataclasses import dataclass, fields, astuple
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"
QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(soup: BeautifulSoup) -> Quote:
    return Quote(
        text=soup.select_one("span.text").text,
        author=soup.select_one("small.author").text,
        tags=[tag.text for tag in soup.select("a.tag")],
    )


def get_quotes_from_page(page_soup: BeautifulSoup) -> List[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(soup) for soup in quotes]


def get_all_quotes() -> List[Quote]:
    print("Start parsing quotes")
    first_page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(first_page, "html.parser")

    all_quotes = get_quotes_from_page(first_page_soup)

    page_number = 2
    while True:
        print(f"Parsing page {page_number}")
        page_url = urljoin(BASE_URL, f"page/{page_number}")
        page = requests.get(page_url).content
        page_soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_quotes_from_page(page_soup))

        if not page_soup.select_one(".next"):
            break

        page_number += 1

    return all_quotes


def write_quotes_to_csv(quotes: [Quote], csv_path: str) -> None:
    with open(csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
