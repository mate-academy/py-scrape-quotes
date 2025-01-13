import csv
import requests
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass
from typing import List


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


def fetch_page_content(url: str) -> BeautifulSoup:
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")


def parse_quote_block(quote_block: Tag) -> Quote:
    return Quote(
        text=quote_block.select_one(".text").text,
        author=quote_block.select_one(".author").text,
        tags=[tag.text for tag in quote_block.select(".tag")]
    )


def scrape_quotes() -> List[Quote]:
    quotes = []
    base_url = "https://quotes.toscrape.com"
    page_url = "/page/1/"

    while page_url:
        soup = fetch_page_content(base_url + page_url)
        quote_blocks = soup.select(".quote")

        for block in quote_blocks:
            quotes.append(parse_quote_block(block))

        next_page = soup.select_one(".next")
        page_url = next_page.select_one("a")["href"] if next_page else None

    return quotes


def save_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csvfile: # noqa E501
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    save_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
