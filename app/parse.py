import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

BASIC_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags > a")],
    )


def parse_single_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes_soup = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes_soup]


def get_all_quotes(basic_url: str) -> list[Quote]:
    page = requests.get(BASIC_URL).content
    page_soup = BeautifulSoup(page, "html.parser")
    quotes = parse_single_page(page_soup)
    next_block = page_soup.select_one(".pager > .next")
    while next_block is not None:
        page = requests.get(
            BASIC_URL + next_block.select_one("a")["href"]
        ).content
        page_soup = BeautifulSoup(page, "html.parser")
        quotes += parse_single_page(page_soup)
        next_block = page_soup.select_one(".pager > .next")
    return quotes


def write_to_csv(quotes: list[Quote], file_name: str) -> None:
    with open(file_name, "w", encoding="utf-8", newline="") as quotes_file:
        writer = csv.writer(quotes_file)
        writer.writerow([field.name for field in fields(Quote)])
        writer.writerows([astuple(quote) for quote in quotes])


def main(file_name: str) -> None:
    quotes = get_all_quotes(BASIC_URL)
    write_to_csv(quotes, file_name)


if __name__ == "__main__":
    main("quotes.csv")
