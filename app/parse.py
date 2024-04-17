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


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=quote_soup.select_one(".tags").text.split()[1:]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> List[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_page_url_with_pagination(page_number: int) -> str:
    return urljoin(BASE_URL, f"page/{page_number}")


def get_quotes() -> List[Quote]:
    first_page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(first_page, "html.parser")

    all_quotes = get_single_page_quotes(page_soup=first_page_soup)

    page_number = 2

    while True:
        next_page_url = get_page_url_with_pagination(page_number)
        next_page = requests.get(next_page_url).content
        next_page_soup = BeautifulSoup(next_page, "html.parser")

        if not next_page_soup.find(class_="next"):
            break

        all_quotes.extend(get_single_page_quotes(page_soup=next_page_soup))
        page_number += 1

    last_page_soup = get_page_url_with_pagination(page_number)
    last_page = requests.get(last_page_soup).content
    last_page_soup = BeautifulSoup(last_page, "html.parser")
    all_quotes.extend(get_single_page_quotes(page_soup=last_page_soup))

    return all_quotes


def write_quotes_to_csv(quotes: [Quote], csv_path: str) -> None:
    with open(csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes=quotes, csv_path=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
