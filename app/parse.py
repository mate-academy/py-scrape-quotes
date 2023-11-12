import csv
from dataclasses import dataclass, fields, astuple
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


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tags .tag")]
    )


def get_all_quotes() -> list[Quote]:
    page = 1
    quotes = []

    while True:
        response = requests.get(urljoin(BASE_URL, f"page/{page}"))
        soup = BeautifulSoup(response.content, "html.parser")

        quotes_soup = soup.select(".quote")
        if not quotes_soup:
            break

        for quote_soup in quotes_soup:
            quotes.append(parse_single_quote(quote_soup))
        page += 1

    return quotes


def write_data_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_data_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
