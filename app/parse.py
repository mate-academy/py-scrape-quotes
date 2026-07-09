import csv
from dataclasses import dataclass
from typing import Generator
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

URL = "https://quotes.toscrape.com/"


@dataclass(frozen=True)
class Quote:
    text: str
    author: str
    tags: list[str]


def page_generator() -> Generator[bytes, None, None]:
    url = URL

    while url:
        response = requests.get(url)
        response.raise_for_status()

        yield response.content

        soup = BeautifulSoup(response.content, "html.parser")
        next_button = soup.select_one("li.next > a")

        if next_button:
            url = urljoin(url, next_button["href"])
        else:
            url = None


def parse_page(content: bytes) -> list[Quote]:
    soup = BeautifulSoup(content, "html.parser")
    quotes: list[Quote] = []

    for quote in soup.select("div.quote"):
        text = quote.select_one("span.text").get_text(strip=True)
        author = quote.select_one("small.author").get_text(strip=True)
        tags = [
            tag.get_text(strip=True)
            for tag in quote.select("div.tags a.tag")
        ]

        quotes.append(
            Quote(
                text=text,
                author=author,
                tags=tags,
            )
        )

    return quotes


def main(output_csv_path: str) -> None:
    quotes: list[Quote] = []

    for page in page_generator():
        quotes.extend(parse_page(page))

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow(
                [
                    quote.text,
                    quote.author,
                    quote.tags,
                ]
            )


if __name__ == "__main__":
    main("quotes.csv")
