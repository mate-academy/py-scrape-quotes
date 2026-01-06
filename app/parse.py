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


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_single_page_quote(soup: Tag) -> list[Quote]:
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> list[Quote]:
    all_quotes = []
    page = 1
    while True:
        time.sleep(1)
        content = requests.get(f"{BASE_URL}/page/{page}/").content
        soup = BeautifulSoup(content, "html.parser")
        all_quotes.extend(get_single_page_quote(soup))

        next_page = soup.select_one(".next")
        if not next_page:
            break
        page += 1

    return all_quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in get_quotes())
