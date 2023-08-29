import csv
from dataclasses import dataclass
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_ULR = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_tags(tags: BeautifulSoup) -> list[str]:
    return [tag.string for tag in tags]


def get_single_quote_data(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=get_tags(quote.select(".tag"))
    )


def get_all_quotes_on_page(page_url: str = None) -> List[Quote] | None:
    page_url = urljoin(BASE_ULR, page_url)
    page = requests.get(page_url).content
    soup = BeautifulSoup(page, "html.parser")
    quotes = soup.select(".quote")
    if quotes:
        return [get_single_quote_data(quote) for quote in quotes]


def get_quote_list():
    quote_list = []
    page_index = 1
    while True:
        data = get_all_quotes_on_page(page_url=f"page/{page_index}/")
        if data is None:
            break
        quote_list.extend(data)
        page_index += 1
    return quote_list


def write_in_the_file(file: str, quote_list: List[Quote]) -> None:
    with open(file, "w", newline="", encoding="utf-8") as file_to_write:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(file_to_write, fieldnames=fieldnames)
        writer.writeheader()
        for quote in quote_list:
            writer.writerow(
                {
                    "text": quote.text,
                    "author": quote.author,
                    "tags": quote.tags
                }
            )


def main(output_csv_path: str) -> None:
    quote_list = get_quote_list()
    write_in_the_file(file=output_csv_path, quote_list=quote_list)


if __name__ == "__main__":
    main("quotes.csv")
