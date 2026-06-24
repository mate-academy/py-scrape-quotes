import csv

from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FILED = [field.name for field in fields(Quote)]


def get_single_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[one.text for one in quote.select(".tag")],
    )


def get_quotes() -> list:
    page = 1
    list_of_quotes = []
    while True:
        content = requests.get(BASE_URL + f"page/{page}/").content
        soup = BeautifulSoup(content, "html.parser")
        quotes = soup.select(".quote")
        list_of_quotes.extend([get_single_quote(quote) for quote in quotes])
        next_page = soup.select_one(".next")
        if not next_page:
            break
        page += 1
    return list_of_quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FILED)
        writer.writerows([astuple(quote) for quote in get_quotes()])


if __name__ == "__main__":
    main("quotes.csv")
