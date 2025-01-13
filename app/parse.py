import csv
from dataclasses import dataclass, fields, astuple
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    tags_block = quote.select_one(".tags")
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in tags_block.find_all("a")]
    )


def get_quotes() -> List[Quote]:
    text = requests.get(BASE_URL).content
    page_soup = BeautifulSoup(text, "html.parser")
    quotes = page_soup.select(".quote")
    all_quotes = [parse_single_quote(quote) for quote in quotes]
    next_page = page_soup.select_one(".next a")

    while next_page:
        url_to_parse = urljoin(BASE_URL, next_page.get("href"))
        text = requests.get(url_to_parse).text
        soup = BeautifulSoup(text, "html.parser")

        quotes = soup.select(".quote")
        all_quotes.extend(parse_single_quote(quote) for quote in quotes)

        next_page = soup.select_one(".next a")

    return all_quotes


def write_quotes_to_csv(quotes: List[Quote]) -> None:
    with open("output_csv_path.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_quotes())


if __name__ == "__main__":
    main("quotes.csv")
