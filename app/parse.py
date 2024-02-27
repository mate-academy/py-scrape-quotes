from dataclasses import dataclass
from urllib.parse import urljoin
from bs4 import BeautifulSoup

import requests
import csv


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"


def parse_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_quotes(number_page: int) -> list[Quote]:
    url = urljoin(BASE_URL, f"page/{number_page}/")

    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    quotes = soup.select(".quote")
    return [parse_quote(quote_soup) for quote_soup in quotes]


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        quote_name = ["text", "author", "tags"]
        writer = csv.DictWriter(file, fieldnames=quote_name)
        writer.writeheader()
        for page in range(1, 11):
            for quote in get_quotes(page):
                writer.writerow(
                    {
                        "text": quote.text,
                        "author": quote.author,
                        "tags": f"{quote.tags}"
                    }
                )


if __name__ == "__main__":
    main("quotes.csv")
