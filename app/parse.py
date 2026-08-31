import csv
from dataclasses import astuple, dataclass, fields
from time import sleep
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
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> list[Quote]:
    quotes = []
    url = BASE_URL

    while url:
        text = requests.get(url).content
        soup = BeautifulSoup(text, "html.parser")

        quotes.extend(get_single_page_quotes(soup))

        next_link = soup.select_one("li.next a")
        if next_link:
            url = urljoin(url, next_link.get("href"))
        else:
            url = None

        sleep(1)

    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()

    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
