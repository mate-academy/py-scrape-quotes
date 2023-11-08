import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup, Tag

QUOTES_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[quote.text for quote in quote_soup.select(".tags > .tag")]
    )


def get_single_page_products(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def check_next_page(page_soup: BeautifulSoup) -> bool:
    if page_soup.select_one(".next") is not None:
        return True
    return False


def get_quotes() -> list[Quote]:
    page = requests.get(QUOTES_URL).content
    page_soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_products(page_soup)

    current_page = 2
    while check_next_page(page_soup):
        page = requests.get(QUOTES_URL + f"/page/{current_page}/").content
        page_soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_products(page_soup))
        current_page += 1

    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
