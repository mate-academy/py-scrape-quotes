import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

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
        tags=[quote.text for quote in quote.select(".tag")],
    )


def get_quotes() -> list[Quote]:
    all_quotes = []
    current_url = BASE_URL
    while True:
        text = requests.get(current_url).text
        page_soup = BeautifulSoup(text, "html.parser")
        quotes = page_soup.select(".quote")
        for quote in quotes:
            all_quotes.append(parse_single_quote(quote))
        next_btn = page_soup.select_one("li.next")
        if next_btn is None:
            break
        current_url = urljoin(BASE_URL, next_btn.select_one("a")["href"])
    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
