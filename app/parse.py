import csv
from dataclasses import dataclass, fields

import requests
from bs4 import BeautifulSoup

URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_tags(tags_soup: BeautifulSoup) -> list[str]:
    return [tag.text for tag in tags_soup]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=parse_tags(quote_soup.select("div.tags > a.tag"))
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> [Quote]:
    all_quotes = []
    for page_num in range(1, 11):
        page = requests.get(f"{URL}/page/{page_num}").content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes += get_single_page_quotes(soup)

    return all_quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows(
            [(quote.text, quote.author, quote.tags) for quote in get_quotes()]
        )


if __name__ == "__main__":
    main("quotes.csv")
