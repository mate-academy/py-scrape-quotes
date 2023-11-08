import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_all_quotes_from_website() -> list[Quote]:
    quotes = []
    page_num = 1

    while True:
        page = requests.get(f"{BASE_URL}/page/{page_num}/").content
        soup = BeautifulSoup(page, "html.parser")

        quotes_data = soup.select(".quote")
        if not quotes_data:
            break

        quotes.extend([get_single_quote(quote) for quote in quotes_data])
        page_num += 1

    return quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes_from_website()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
