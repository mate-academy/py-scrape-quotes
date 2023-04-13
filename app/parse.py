import codecs
import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, element

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: element.Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag_soup.text for tag_soup in quote_soup.select(".tags > a")],
    )


def get_page_quotes(url: str, quotes: list[Quote]) -> None:
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")

    quotes.extend(
        [
            parse_single_quote(quote_soup)
            for quote_soup in soup.select(".quote")
        ]
    )

    next_page = soup.select_one(".pager > .next > a")
    if next_page is not None:
        get_page_quotes(urljoin(BASE_URL, next_page["href"]), quotes)


def get_all_quotes() -> list[Quote]:
    quotes = []
    get_page_quotes(BASE_URL, quotes)

    return quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with codecs.open(output_csv_path, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    print(quotes)
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
