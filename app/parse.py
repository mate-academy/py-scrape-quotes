import csv
import time
from dataclasses import dataclass, asdict
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_quotes(soup: BeautifulSoup) -> list[Quote]:
    quotes = []

    for item in soup.select(".quote"):
        text = item.select_one(".text").get_text(strip=True)
        author = item.select_one(".author").get_text(strip=True)
        tags = [
            tag.get_text(strip=True)
            for tag in item.select(".tag")
        ]

        quotes.append(Quote(text, author, tags))

    return quotes


def get_all_quotes() -> list[Quote]:
    quotes = []
    url = BASE_URL

    with requests.Session() as session:
        while url:
            response = session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            quotes.extend(parse_quotes(soup))

            next_page = soup.select_one(".next a")

            if next_page:
                url = urljoin(url, next_page["href"])
                time.sleep(1)
            else:
                url = None

    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["text", "author", "tags"],
        )
        writer.writeheader()
        writer.writerows(asdict(quote) for quote in quotes)


if __name__ == "__main__":
    main("quotes.csv")
