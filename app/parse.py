import csv
from dataclasses import dataclass, fields, astuple
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_single_quote(quote_soup: BeautifulSoup) -> Quote:
    tags = quote_soup.select_one(".tags").text.split()[1:]
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=tags
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> List[Quote]:
    quotes = page_soup.select(".quote")

    return [get_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> List[Quote]:
    first_page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(first_page, "html.parser")

    all_quotes = get_single_page_quotes(page_soup=first_page_soup)

    page_number = 2

    while True:
        next_page_url = urljoin(BASE_URL, f"page/{page_number}")
        next_page = requests.get(next_page_url).content
        next_page_soup = BeautifulSoup(next_page, "html.parser")

        if not next_page_soup.find(class_="next"):
            break

        all_quotes.extend(get_single_page_quotes(page_soup=next_page_soup))
        page_number += 1

    last_page_soup = urljoin(BASE_URL, f"page/{page_number}")
    last_page = requests.get(last_page_soup).content
    last_page_soup = BeautifulSoup(last_page, "html.parser")
    all_quotes.extend(get_single_page_quotes(page_soup=last_page_soup))

    return all_quotes


def write_to_csv(quotes: List[Quote], csv_path: str) -> None:
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_to_csv(quotes=quotes, csv_path=output_csv_path)


if __name__ == "__main__":
    main("result.csv")
