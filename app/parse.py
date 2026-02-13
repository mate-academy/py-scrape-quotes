from dataclasses import dataclass
from typing import List
import requests
from bs4 import BeautifulSoup
import csv
import time


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


def parse_quotes_from_page(soup: BeautifulSoup) -> List[Quote]:
    quotes = []

    for quote_block in soup.find_all("div", class_="quote"):
        text = quote_block.find("span", class_="text").get_text(strip=True)
        author = quote_block.find("small", class_="author").get_text(strip=True)
        tags = [
            tag.get_text(strip=True)
            for tag in quote_block.find_all("a", class_="tag")
        ]

        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def get_next_page(soup: BeautifulSoup) -> str | None:
    next_btn = soup.find("li", class_="next")
    if next_btn:
        next_href = next_btn.find("a")["href"]
        return BASE_URL + next_href
    return None


def main(output_csv_path: str) -> None:
    url = BASE_URL
    all_quotes: List[Quote] = []

    while url:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        quotes = parse_quotes_from_page(soup)
        all_quotes.extend(quotes)

        url = get_next_page(soup)

        time.sleep(0.3)

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])

        for quote in all_quotes:
            writer.writerow([
                quote.text,
                quote.author,
                ", ".join(quote.tags),
            ])


if __name__ == "__main__":
    main("quotes.csv")
