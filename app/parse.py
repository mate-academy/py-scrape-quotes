import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text.strip() for tag in quote.select("div.tags > a.tag")]
    )


def get_single_page(page: bytes) -> list[Quote]:
    soup = BeautifulSoup(page, "html.parser")
    quotes = soup.select("div.quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_pages() -> list[Quote]:
    page_number = 1
    all_page_quotes = []
    while True:
        page = requests.get(BASE_URL + f"/page/{page_number}/")
        if page.status_code != 200:
            break
        page_number += 1
        single_page_quotes = get_single_page(page.content)
        if not single_page_quotes:
            break
        all_page_quotes.extend(single_page_quotes)
    return all_page_quotes


def write_quotes_to_csv(quotes: [Quote], filename: str) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_pages()
    write_quotes_to_csv(quotes=quotes, filename=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
