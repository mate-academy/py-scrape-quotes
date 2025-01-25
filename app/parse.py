import dataclasses
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, Tag
import csv


BASE_URL = "https://quotes.toscrape.com/page/{}/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in dataclasses.fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    text_element = quote.select_one(".text")
    author_element = quote.select_one(".author")
    tag_elements = quote.select(".tag")

    text = text_element.get_text(strip=True) if text_element else None
    author = author_element.get_text(strip=True) if author_element else None
    tags = (
        [tag.get_text(strip=True) for tag in tag_elements]
        if tag_elements
        else []
    )

    return Quote(
        text=text,
        author=author,
        tags=tags,
    )


def get_quotes_data() -> [Quote]:
    page_number = 1
    quotes = []

    while True:
        url = BASE_URL.format(page_number)
        response = requests.get(url)
        page_soup = BeautifulSoup(response.content, "html.parser")

        quotes_on_page = page_soup.select(".quote")
        quotes.extend([parse_single_quote(quote) for quote in quotes_on_page])

        next_button = page_soup.select_one(".pager .next a")
        if not next_button:
            break

        page_number += 1

    return quotes


def write_to_csv(path: str, quotes: [Quote]) -> None:
    with open(path, "w", encoding="utf8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([dataclasses.astuple(quote) for quote in quotes])


def main(path: str) -> None:
    write_to_csv(path, get_quotes_data())


if __name__ == "__main__":
    main("result.csv")
