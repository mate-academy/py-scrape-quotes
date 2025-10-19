import csv
from dataclasses import dataclass
from typing import Generator
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page(page_url: str) -> bytes | None:
    response = requests.get(page_url)
    if response.status_code == 200:
        return response.content
    return None


def page_generator() -> Generator[BeautifulSoup, None, None]:
    page_number = 1
    while True:
        page_url = urljoin(URL, f"page/{page_number}/")
        content = fetch_page(page_url)
        if not content:
            break
        soup = BeautifulSoup(content, "html.parser")
        if not soup.select(".quote"):
            break
        yield soup
        page_number += 1


def parse_single_quote(element: Tag) -> Quote:
    text = element.select_one(".text").text.strip()
    author = element.select_one(".author").text.strip()
    tags = [tag.text.strip() for tag in element.select(".tag")]
    return Quote(text=text, author=author, tags=tags)


def parse_page(page: BeautifulSoup) -> list[Quote]:
    result = []
    for element in page.select(".quote"):
        result.append(parse_single_quote(element))
    return result


def get_quotes() -> list[Quote]:
    quotes = []
    for page in page_generator():
        quotes.extend(parse_page(page))
    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


if __name__ == "__main__":
    main("quotes.csv")
