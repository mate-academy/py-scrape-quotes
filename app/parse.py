import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

HOME_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


PRODUCT_FIELDS = [field.name for field in fields(Quote)]


def get_all_quotes_tags() -> list[Tag]:
    page_number = 1
    all_quotes = []
    while True:
        url = urljoin(HOME_URL, f"/page/{page_number}")
        text = requests.get(url).content
        soup = BeautifulSoup(text, "html.parser")

        quotes = get_quotes_from_page(soup)
        if not quotes:
            break

        all_quotes.extend(quotes)
        page_number += 1
    return all_quotes


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one("[itemprop='text']").text,
        author=quote.select_one("[itemprop='author']").text,
        tags=[tag.text for tag in quote.select(".tags a.tag")],
    )


def get_quotes_from_page(soup: BeautifulSoup) -> list[Tag]:
    quotes = soup.select(".quote")
    return quotes


def get_quotes_objects() -> list[Quote]:
    return [parse_single_quote(quote) for quote in get_all_quotes_tags()]


def write_to_csv(name: str) -> None:
    with open(name, "w") as file:
        writer = csv.writer(file)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows([astuple(quote) for quote in get_quotes_objects()])


def main(output_csv_path: str) -> None:
    write_to_csv(output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
