import csv
import requests
from dataclasses import dataclass
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    quote_text = quote_soup.select_one(".text").text
    quote_author = quote_soup.select_one(".author").text
    tags = quote_soup.select_one(".keywords")["content"]
    if tags:
        quote_tags = tags.split(",")
    else:
        quote_tags = []

    return Quote(quote_text, quote_author, quote_tags,)


def get_single_page_quotes(quote_soup: BeautifulSoup) -> [Quote]:
    quotes = quote_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_page_url(page_number: str = "1") -> str:
    return urljoin(BASE_URL, f"page/{page_number}/")


def get_quotes() -> [Quote]:
    page_number = 1
    first_page = requests.get(get_page_url()).content
    first_page_soup = BeautifulSoup(first_page, "html.parser")
    all_quotes = get_single_page_quotes(first_page_soup)
    next_page_is = first_page_soup.select_one(".pager li.next")

    while next_page_is:
        page_number += 1
        page_url = get_page_url(str(page_number))
        page = requests.get(page_url).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        try:
            next_page_is = soup.select_one(".pager li.next")
        except AttributeError:
            next_page_is = None

    return all_quotes


def main(output_csv_path: str) -> None:
    print(get_quotes())
    quotes = get_quotes()
    with open(
            output_csv_path,
            "w",
            newline="",
            encoding="utf-8"
    ) as csvfile:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for quote in quotes:
            writer.writerow(
                {
                    "text": quote.text,
                    "author": quote.author,
                    "tags": quote.tags,
                }
            )


if __name__ == "__main__":
    main("quotes.csv")
