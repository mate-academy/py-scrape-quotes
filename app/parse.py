import csv
import time
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = fields(Quote)


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def parse_quotes_from_one_page(page: BeautifulSoup) -> list[Quote]:
    return [parse_single_quote(quote) for quote in page.select(".quote")]


def parse_quotes() -> list[Quote]:
    text = requests.get(BASE_URL).content
    page = BeautifulSoup(text, "html.parser")
    all_quotes = parse_quotes_from_one_page(page)
    num_pages = 2
    while page.select_one(".next") is not None:
        time.sleep(1)
        text = requests.get(f"{BASE_URL}/page/{num_pages}").content
        page = BeautifulSoup(text, "html.parser")
        all_quotes.extend(parse_quotes_from_one_page(page))
        num_pages += 1
    return all_quotes


def write_csv_file(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([field.name for field in QUOTE_FIELDS])
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_csv_file(parse_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
