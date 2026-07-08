import csv
import time
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


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").get_text(strip=True),
        author=quote_soup.select_one(".author").get_text(strip=True),
        tags=[tag.get_text() for tag in quote_soup.select(".tag")],
    )


def parse_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    page_number = 1

    while True:
        url = f"{BASE_URL}page/{page_number}/"
        response = requests.get(url)
        page_soup = BeautifulSoup(response.content, "html.parser")

        all_quotes.extend(parse_page(page_soup))

        next_button = page_soup.select_one("li.next > a")
        if next_button is None:
            break

        page_number += 1
        time.sleep(0.1)

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
