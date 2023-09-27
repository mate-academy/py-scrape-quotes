import csv
from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup, ResultSet

import requests

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
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def parse_single_page(target_page: ResultSet) -> list[Quote]:
    return [parse_single_quote(quote) for quote in target_page]


def parse_website() -> list[Quote]:
    page = 1
    parsed_pages = []
    while True:
        response = requests.get(urljoin(BASE_URL, f"page/{page}")).content
        target_page = BeautifulSoup(response, "html.parser")
        target_page = target_page.select(".quote")
        if not target_page:
            break
        parsed_page = parse_single_page(target_page)
        parsed_pages.extend(parsed_page)
        page += 1
    return parsed_pages


def main(output_csv_path: str) -> None:
    quotes_list = parse_website()
    with open(output_csv_path, "w", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes_list:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
