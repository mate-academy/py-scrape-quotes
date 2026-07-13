from dataclasses import dataclass, astuple, fields
import csv
import time

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags .tag")],
    )


def get_quotes_from_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    page_url = BASE_URL

    with requests.Session() as session:
        while page_url:
            response = session.get(page_url)
            response.raise_for_status()
            page_soup = BeautifulSoup(response.content, "html.parser")

            all_quotes.extend(get_quotes_from_page(page_soup))

            next_button = page_soup.select_one(".next > a")
            page_url = BASE_URL + next_button["href"] if next_button else None

            time.sleep(0.5)

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
