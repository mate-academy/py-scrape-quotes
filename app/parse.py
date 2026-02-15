import csv
from dataclasses import dataclass, fields
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
    tags = [tag.text for tag in quote.select(".tag")]
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=tags
    )


def get_quotes_for_all_pages() -> list[Quote]:
    all_quotes = []
    current_url = BASE_URL
    page_number = 1

    while current_url:
        text = requests.get(current_url).content
        soup = BeautifulSoup(text, "html.parser")
        quotes_on_page = soup.select(".quote")
        for quote in quotes_on_page:
            all_quotes.append(parse_single_quote(quote))

        next_button = soup.select_one("li.next a")

        if next_button:
            current_url = urljoin(BASE_URL, next_button["href"])
            page_number += 1
        else:
            current_url = None

    return all_quotes


def get_all_quotes() -> list[Quote]:
    text = requests.get(BASE_URL).content
    soup = BeautifulSoup(text, "html.parser")
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_quotes_for_all_pages(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
