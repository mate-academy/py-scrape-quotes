from dataclasses import dataclass, fields, astuple

from bs4 import BeautifulSoup

import csv

import requests

BASE_URL = "https://quotes.toscrape.com/"
PAGE_URL = BASE_URL + "page/{page_number}"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> [Quote]:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_page_content(page_number: int) -> [BeautifulSoup]:
    page = requests.get(PAGE_URL.format(page_number=page_number)).content
    page_content = BeautifulSoup(page, "html.parser")
    return page_content


def get_quotes() -> [BeautifulSoup]:
    page_number = 1
    all_quotes = get_page_content(page_number).select(".quote")
    pagination = get_page_content(page_number).select(".next")

    while pagination:
        page_number += 1
        all_quotes.extend(get_page_content(page_number).select(".quote"))
        pagination = get_page_content(page_number).select(".next")

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(
            [astuple(parse_single_quote(quote)) for quote in quotes]
        )


if __name__ == "__main__":
    main("quotes.csv")
