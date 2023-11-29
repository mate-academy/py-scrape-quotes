import csv
import requests

from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com/"
QOUTES_OUTPUT_CSV_PATH = "quotes.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> [Quote]:
    first_page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(first_page, "html.parser")
    quotes = get_single_page_quotes(first_page_soup)
    next_page = first_page_soup.select_one(".next > a")

    while next_page is not None:
        page = requests.get(urljoin(BASE_URL, next_page.get("href"))).content
        soup = BeautifulSoup(page, "html.parser")

        quotes.extend(get_single_page_quotes(soup))
        next_page = soup.select_one(".next > a")

    return quotes


def write_quotes_to_csv(quotes: [Quote]) -> None:
    with open(
            QOUTES_OUTPUT_CSV_PATH, "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    qoutes = get_quotes()
    write_quotes_to_csv(qoutes)


if __name__ == "__main__":
    main(QOUTES_OUTPUT_CSV_PATH)
