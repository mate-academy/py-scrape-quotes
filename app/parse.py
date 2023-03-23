import csv
import urllib.parse

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass


QUOTE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_quote_tags(quote_soup: BeautifulSoup) -> list[str]:
    tags = quote_soup.select_one(".tags")
    return [
        tag.text for tag in tags.select(".tag")
    ]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=parse_quote_tags(quote_soup)
    )


def parse_quotes(quotes_soup: BeautifulSoup) -> [Quote]:
    return [
        parse_single_quote(quote) for quote in quotes_soup
    ]


def main(output_csv_path: str) -> None:
    page = requests.get(QUOTE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    with open(output_csv_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        while True:

            quotes = soup.select(".quote")
            quotes_parsed = parse_quotes(quotes)

            for quote in quotes_parsed:
                writer.writerow(
                    [quote.text, quote.author, quote.tags],
                )
            if soup.select_one(".next"):
                page_url = urllib.parse.urljoin(
                    QUOTE_URL, soup.select_one(".next > a")["href"]
                )
                page = requests.get(page_url).content
                soup = BeautifulSoup(page, "html.parser")
            else:
                break


if __name__ == "__main__":
    main("quotes.csv")
