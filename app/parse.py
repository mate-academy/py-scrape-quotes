import csv

import requests

from dataclasses import dataclass, astuple
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    tag_elements = quote_soup.select(".tags .tag")
    tag_names = [tag.text for tag in tag_elements]

    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=tag_names
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> [Quote]:
    all_quotes = []

    page_number = 1

    while True:
        print(page_number)
        url = f"{BASE_URL}/page/{page_number}/"
        page = requests.get(url).content

        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))

        if soup.select_one(".next"):
            page_number += 1
        else:
            break

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
