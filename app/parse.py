import csv
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup

URL = "https://quotes.toscrape.com/"
URL_FOR_PARSE = URL + "/page/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


page = requests.get(URL).content
soup = BeautifulSoup(page, "html.parser")


def get_all_quotes() -> List[Quote]:
    all_pages = []
    num_of_page = 1

    while True:
        page = requests.get(URL_FOR_PARSE + str(num_of_page)).content
        soup = BeautifulSoup(page, "html.parser")

        all_pages.extend(get_all_quotes_from_single_page(soup))

        if soup.select_one(".next") is None:
            break

        num_of_page += 1

    return all_pages


def get_all_quotes_from_single_page(soup: BeautifulSoup) -> [Quote]:
    quotes = []
    quotes_on_page = soup.select(".quote")
    for quote in quotes_on_page:
        quote1 = Quote(
            text=quote.select_one(".text").text,
            author=quote.select_one(".author").text,
            tags=[tag.text for tag in quote.select(".tag")],
        )
        quotes.append(quote1)
    return quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
    for item in get_all_quotes():
        with open(output_csv_path, "a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([item.text, item.author, item.tags])


if __name__ == "__main__":
    main("quotes.csv")
