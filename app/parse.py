import csv
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_all_quotes() -> [Quote]:
    result = []
    num_page = 1
    while True:
        pagination_url = urljoin(BASE_URL, f"/page/{num_page}")
        page = requests.get(pagination_url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = soup.select(".quote")
        result += [parse_single_quote(quote) for quote in quotes]
        num_page += 1
        if not soup.select(".pager > .next"):
            break
    return result


def writing_csv(path: str, quotes: [Quote]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    writing_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
