import csv

import requests
from dataclasses import dataclass, fields
from bs4 import BeautifulSoup


QUOTES_URL = "https://quotes.toscrape.com/"

QUOTES_OUTPUT_CSV_PATH = "quotes.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[element.text for element in quote_soup.select(".tags a.tag")]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    products = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in products]


def get_all_quotes() -> [Quote]:
    page = requests.get(QUOTES_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(first_page_soup)
    current_page = 2
    while True:
        page = requests.get(QUOTES_URL + f"page/{current_page}/").content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))

        current_page += 1
        if not soup.select("li.next"):
            break
    return all_quotes


def write_products_to_csv(output_csv_path: str, quotes: [Quote]) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=QUOTES_FIELDS)

        writer.writeheader()
        for quote in quotes:
            writer.writerow(
                {
                    "text": quote.text,
                    "author": quote.author,
                    "tags": quote.tags
                }
            )


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_products_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
