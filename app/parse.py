import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").get_text()
    tags = [tag.get_text() for tag in quote_soup.select(".tag")]
    return Quote(text=text, author=author, tags=tags)


def get_page_content(url: str) -> BeautifulSoup:
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")


def get_all_quotes() -> list[Quote]:
    quotes = []
    url = BASE_URL
    while url:
        soup = get_page_content(url)
        quote_elements = soup.select(".quote")
        for quote_soup in quote_elements:
            quotes.append(parse_single_quote(quote_soup))
        next_button = soup.select_one("li.next > a")
        if next_button:
            next_url = next_button.get("href")
            url = BASE_URL + next_url
        else:
            url = None
    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        for quote in quotes:
            writer.writerow({
                "text": quote.text,
                "author": quote.author,
                "tags": str(quote.tags)
            })


if __name__ == "__main__":
    main("result.csv")
