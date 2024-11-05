import csv
from dataclasses import dataclass, astuple, fields

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_ROWS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one("span.text").text,
        author=quote_soup.select_one("small.author").text,
        tags=[tag.get_text() for tag in quote_soup.select(".tags > a.tag")],
    )


def get_quotes_from_single_page(soup: BeautifulSoup) -> list[Quote]:
    quotes = []

    products = soup.select(".quote")
    for product in products:
        quote = parse_single_quote(product)
        quotes.append(quote)
    return quotes


def parse_pagination() -> list[Quote]:
    results = []
    counter = 1
    while requests.get(f"{BASE_URL}/page/{counter}/").status_code == 200:
        print(f"parsed page #{counter}")
        page = requests.get(f"{BASE_URL}/page/{counter}/").content
        soup = BeautifulSoup(page, "html.parser")
        if not get_quotes_from_single_page(soup):
            break
        else:
            results.extend(get_quotes_from_single_page(soup))
        counter += 1
    return results


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_ROWS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(output_csv_path, parse_pagination())


if __name__ == "__main__":
    main("quotes.csv")
