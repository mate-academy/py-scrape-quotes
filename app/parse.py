import csv
from dataclasses import dataclass, astuple, fields
import time

import requests

from bs4 import BeautifulSoup, Tag

HOME_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one('.text').text,
        author=quote.select_one('.author').text,
        tags=[element.text for element in quote.select(".tag")]
    )


def parse_page(page: Tag) -> list[Quote]:
    quotes = page.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_next(page: Tag) -> bool:
    return bool(page.select_one(".next"))


def get_all_quotes() -> list[Quote]:
    page = 1
    all_quotes = []
    have_next = True
    while have_next:
        url = HOME_URL + f"/page/{page}/"
        curr = requests.get(url).content
        soup = BeautifulSoup(curr, "html.parser")
        have_next = get_next(soup)
        all_quotes.extend(parse_page(soup))
        page += 1
        time.sleep(1)
    return all_quotes


def write_to_file(all_quotes: list[Quote], output_csv_path) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in all_quotes])


def main(output_csv_path: str) -> None:
    write_to_file(get_all_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
