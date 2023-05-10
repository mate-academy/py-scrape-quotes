from dataclasses import dataclass
from typing import List

import requests
import csv
from bs4 import BeautifulSoup


url = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    text = quote.find(class_="text").get_text()
    author = quote.find(class_="author").get_text()
    tags = [tag.get_text() for tag in quote.find_all(class_="tag")]

    return Quote(text, author, tags)


def write_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def scrape_quotes(url: str) -> List[Quote]:
    quotes = []
    page_num = 1
    while True:
        page = requests.get(f"{url}/page/{page_num}/")
        soup = BeautifulSoup(page.content, "html.parser")
        quotes_on_page = soup.find_all(class_="quote")
        if not quotes_on_page:
            break
        for quote in quotes_on_page:
            quotes.append(parse_single_quote(quote))
        page_num += 1
    return quotes


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes(url)
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
