import requests
from bs4 import BeautifulSoup, Tag
import csv

from dataclasses import dataclass

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_single_quotes(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [get_single_quotes(quotes_soup) for quotes_soup in quotes]


def parse_quotes(url: str) -> [Quote]:
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    all_quotes = get_single_page_quotes(soup)

    while True:
        if soup.select(".next"):
            page = requests.get(
                url + soup.select_one("li.next a")["href"]
            ).content
            soup = BeautifulSoup(page, "html.parser")
            all_quotes.extend(get_single_page_quotes(soup))
        else:
            return all_quotes


def create_csv(quotes: [Quote]) -> None:
    with open("result.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for quote in quotes:
            writer.writerow({
                "text": quote.text,
                "author": quote.author,
                "tags": quote.tags,
            })


def main(output_csv_path: str) -> None:
    pass


if __name__ == "__main__":
    create_csv(parse_quotes(BASE_URL))
    main("result.csv")
