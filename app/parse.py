import csv
import requests

from dataclasses import dataclass
from bs4 import BeautifulSoup

PAGES_URL = "https://quotes.toscrape.com/page/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_quotes() -> list[Quote]:
    quotes_list = []

    page_num = 1
    quotes = BeautifulSoup(
        requests.get(f"{PAGES_URL}{page_num}/").content,
        "html.parser"
    ).select(".quote")

    while quotes:
        for quote in quotes:
            quotes_list.append(Quote(
                text=quote.select_one(".text").text,
                author=quote.select_one(".author").text,
                tags=[tag.text for tag in quote.select(".tag")]
            ))

        page_num += 1
        quotes = BeautifulSoup(
            requests.get(f"{PAGES_URL}{page_num}/").content,
            "html.parser"
        ).select(".quote")

    return quotes_list


def main(output_csv_path: str) -> None:

    with open(output_csv_path, "w", newline="") as csv_quotes:
        headers = ["text", "author", "tags"]
        writer = csv.writer(csv_quotes)
        writer.writerow(headers)
        for quote in get_quotes():
            writer.writerow(
                [quote.text, quote.author, quote.tags]
            )


if __name__ == "__main__":
    main("quotes.csv")
