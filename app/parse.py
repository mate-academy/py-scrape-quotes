import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text[1:-1],
        author=quote_soup.select_one(".author").text,
        tags=quote_soup.select_one(".tags > .keywords")["content"].split(","),
    )


def get_single_page_quotes(quote_soup: BeautifulSoup) -> [Quote]:
    quotes = quote_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> [Quote]:
    next_page_link = BASE_URL + "page/1/"
    all_quotes = []

    while True:
        page = requests.get(next_page_link).content
        main_soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(main_soup))

        next_page_link_element = main_soup.select_one("nav li.next a")
        if not next_page_link_element:
            break

        next_page_link = BASE_URL + next_page_link_element["href"][1:]

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    with open(
        output_csv_path, mode="w", newline="", encoding="utf-8"
    ) as csv_file:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for quote in quotes:
            writer.writerow(
                {
                    "text": quote.text,
                    "author": quote.author,
                    "tags": ", ".join(quote.tags),
                }
            )


if __name__ == "__main__":
    main("quotes.csv")
