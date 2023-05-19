import csv
from dataclasses import dataclass, fields
from typing import List

from bs4 import BeautifulSoup, Tag

import requests

BASE_URL = "https://quotes.toscrape.com/"
PAGE_URL = BASE_URL + "page/{page_number}"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quotes(quotes_soup: Tag) -> Quote:
    return (Quote(
        text=quotes_soup.select_one(".text").text,
        author=quotes_soup.select_one(".author").text,
        tags=[tag.text for tag in quotes_soup.select(".tag")]
    ))


def get_single_page_quotes(quote_soup: BeautifulSoup) -> [Quote]:
    quotes = quote_soup.select(".quote")
    return [parse_single_quotes(quote_soup)
            for quote_soup in quotes]


def get_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    result = get_single_page_quotes(soup)
    page_num = 2
    while soup.select_one(".next") is not None:
        page = requests.get(
            PAGE_URL.format(page_number=page_num)
        ).content
        soup = BeautifulSoup(page, "html.parser")
        result.extend(get_single_page_quotes(soup))
        page_num += 1

    return result


def write_to_csv(quotes: List[Quote],
                 output_csv_path: str) -> None:
    with open(output_csv_path, "w",
              encoding="utf-8",
              newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
