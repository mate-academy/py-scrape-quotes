import csv

import requests
from dataclasses import dataclass, fields, astuple

from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_page(quote: Tag) -> Quote:
    quote_tags = quote.select(".tag")
    return Quote(
        text=quote.select_one(".text").text.replace("“", "").replace("”", ""),
        author=quote.select_one(".author").text,
        tags=[tag.get_text() for tag in quote_tags],
    )


def get_single_page_quotes(page_soup: Tag) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_page(quote) for quote in quotes]


def get_quotes() -> [Quote]:
    text = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(text, "html.parser")
    all_quotes = get_single_page_quotes(first_page_soup)

    num_pages = 10
    for page_num in range(2, num_pages + 1):
        text = requests.get(BASE_URL + f"page/{page_num}").content
        next_page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(next_page_soup))

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    with open(
            f"{output_csv_path}", "w",
            encoding="utf-8",
            newline=""
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
