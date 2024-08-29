import csv
from dataclasses import (
    astuple,
    dataclass,
    fields
)

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_page_quotes(page_num: int) -> BeautifulSoup:
    url = f"{BASE_URL}page/{page_num}"
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    return soup


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag_soup.text for tag_soup in quote_soup.select(".tags > .tag")]
    )


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    page_num = 1

    while True:
        url = f"{BASE_URL}page/{page_num}"
        soup = get_page_quotes(page_num)
        quotes = [parse_single_quote(quote_soup) for quote_soup in soup.select(".quote")]
        all_quotes.extend(quotes)

        if not soup.select_one(".pager > .next"):
            break
        page_num += 1

    return all_quotes


def write_to_csv(filename: str) -> None:
    all_quotes = get_all_quotes()
    with open(filename, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in all_quotes])


def main(output_csv_path: str) -> None:
    write_to_csv(output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
