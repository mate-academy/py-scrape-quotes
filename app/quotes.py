import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from app.authors import get_author, Author

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: Author
    tags: list[str]


def get_single_quote(soup: BeautifulSoup) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=get_author(soup),
        tags=[
            soup_tag.text
            for soup_tag
            in soup.select(".tag")
        ]
    )


def get_quote_list(soup: BeautifulSoup) -> [Quote]:
    return [
        get_single_quote(quote_soup)
        for quote_soup
        in soup.select(".quote")
    ]


def get_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    page_soup = BeautifulSoup(page, "html.parser")
    page_num = 0

    quotes = []

    while page_soup.select(".next"):
        page_num += 1
        current_page_url = BASE_URL + f"page/{page_num}/"
        page = requests.get(current_page_url).content
        page_soup = BeautifulSoup(page, "html.parser")

        quotes.extend(get_quote_list(page_soup))

    return quotes


def create_quotes_csv_file(file_name: str) -> None:
    with open(
            file_name,
            "w",
            newline="",
            encoding="utf-8"
    ) as csvfile:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for quote in get_quotes():
            writer.writerow({
                "text": quote.text,
                "author": quote.author.name,
                "tags": quote.tags
            })
