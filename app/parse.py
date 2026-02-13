import csv
from dataclasses import dataclass
from typing import Generator

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


URL = "https://quotes.toscrape.com/"


def page_generator() -> Generator[BeautifulSoup, None, None]:
    page_number = 1

    with requests.Session() as session:

        while True:
            request_url = f"{URL}page/{page_number}/"
            response = session.get(request_url)
            soup = BeautifulSoup(response.content, "html.parser")

            if response.status_code != 200 or not soup.select(".quote"):
                print("The end, folks!")
                break

            yield soup

            page_number += 1


def parse_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = []

    for quote in page_soup.select(".quote"):
        quotes.append(parse_single_quote(quote))

    return quotes


def parse_single_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags = []
    for tag in quote.select(".tag"):
        tags.append(tag.text)

    return Quote(
        text=text,
        author=author,
        tags=tags
    )


def get_quotes() -> list[Quote]:
    quotes = []
    for page_soup in page_generator():
        parsed_quotes = parse_page(page_soup)
        quotes.extend(parsed_quotes)
    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()

    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, ",".join(quote.tags)])


if __name__ == "__main__":
    main("quotes.csv")
