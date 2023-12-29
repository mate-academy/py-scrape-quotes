import csv
import requests

from bs4 import BeautifulSoup
from dataclasses import dataclass


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_page(url: str) -> bytes:
    return requests.get(url).content


def parse_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=str(quote.select_one(".text").text),
        author=str(quote.select_one(".author").text),
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_quotes() -> list[Quote]:
    """ Function to parse quotes with pagination handling """

    soup = BeautifulSoup(get_page(BASE_URL), "html.parser")
    quotes = []

    page_count = 1
    while (soup.select_one(".next")
           or (soup.select_one(".previous") and soup.select_one(".next"))):
        quotes += soup.select(".quote")

        page_count += 1
        soup = BeautifulSoup(
            get_page(BASE_URL + f"/page/{page_count}/"),
            "html.parser"
        )

    soup = BeautifulSoup(
        get_page(BASE_URL + f"/page/{page_count}/"),
        "html.parser"
    )
    quotes += soup.select(".quote")

    return [parse_quote(quote) for quote in quotes]


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])

        writer.writerows([
            [quote.text, quote.author, quote.tags.__repr__()]
            for quote in get_quotes()
        ])


if __name__ == "__main__":
    main("quotes.csv")
