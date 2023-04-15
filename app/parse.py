import csv
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [quote.name for quote in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> list[Quote]:
    page = requests.get(BASE_URL).content
    all_quotes = []

    while True:
        page_soup = BeautifulSoup(page, "html.parser")
        all_quotes += get_single_page_quotes(page_soup)

        if page_soup.select_one(".next") is None:
            break

        next_page_link = urljoin(
            BASE_URL, page_soup.select_one(".next > a")["href"]
        )
        page = requests.get(next_page_link).content

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="") as file_output:
        writer = csv.writer(file_output)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
