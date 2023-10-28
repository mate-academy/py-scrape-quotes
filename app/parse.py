import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_tags(tags_soup: BeautifulSoup) -> list[str]:
    tags = tags_soup.select(".keywords")[0]["content"]
    if tags:
        return tags.split(",")
    return []


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=parse_tags(quote_soup),
    )


def get_single_page(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_info() -> [Quote]:
    page_num = 1
    all_quotes = []

    while True:
        url = BASE_URL + f"page/{page_num}/"
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page(soup))
        page_num += 1
        next_page = soup.select_one(".next")
        if next_page is None:
            break

    return all_quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        all_quotes = get_info()
        writer.writerows([astuple(quote) for quote in all_quotes])


if __name__ == "__main__":
    main("quotes.csv")
