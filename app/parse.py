import csv
import requests

from dataclasses import dataclass
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_quotes(page: int = 19) -> list[Quote]:
    quotes = BeautifulSoup(
        requests.get(f"{BASE_URL}/page/{page}").content,
        "html.parser"
    ).select(".quote")

    return [parse_quote(quote) for quote in quotes]


def main(output_csv_path: str) -> None:
    page = 1
    result = []

    while True:
        new_quotes = get_quotes(page)

        if len(new_quotes):
            result.extend(new_quotes)
            page += 1
            print(page)
        else:
            break

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(["text", "author", "tags"])

        for quote in result:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
