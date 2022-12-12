import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
CSV_PATH = "quotes.csv"


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
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> Quote:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> Quote:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    quotes = get_single_page_quotes(soup)
    page_num = 2

    while soup.select(".next"):
        page_content = requests.get(f"{BASE_URL}page/{page_num}/").content
        soup = BeautifulSoup(page_content, "html.parser")
        quotes.extend(get_single_page_quotes(soup))
        page_num += 1

    return quotes


def write_quotes_to_csv(quotes: [Quote], csv_path: str) -> None:
    with open(csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(text) for text in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()

    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main(CSV_PATH)
