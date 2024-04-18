import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"


def scrape_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def scrape_page(url: str, page_num: int) -> [Quote]:
    page_url = f"page/{page_num}/"
    response = requests.get(url + page_url)
    soup = BeautifulSoup(response.content, "html.parser")

    return [
        scrape_single_quote(quote)
        for quote in soup.select(".quote")
    ]


def scrape_all_pages(url: str) -> [Quote]:
    page_num = 1
    all_quotes = []

    while True:
        quotes = scrape_page(url, page_num)

        if not quotes:
            return all_quotes

        all_quotes.extend(quotes)
        page_num += 1


def main(output_csv_path: str) -> None:
    quotes = scrape_all_pages(BASE_URL)

    with open(output_csv_path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["text", "author", "tags"])
        writer.writerow({"text": "text", "author": "author", "tags": "tags"})

        [
            writer.writerow(
                {
                    "text": quote.text,
                    "author": quote.author,
                    "tags": quote.tags
                }
            )
            for quote in quotes
        ]


if __name__ == "__main__":
    main("quotes.csv")
