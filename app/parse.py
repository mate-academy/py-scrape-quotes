from dataclasses import dataclass
import csv
from pathlib import Path
from bs4 import BeautifulSoup
import requests

BASE_DIR = Path(__file__).resolve().parent
BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page(url: str) -> None:
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    return None


def parse_quotes(page_content: str) -> list:
    quotes = []
    soup = BeautifulSoup(page_content, "html.parser")
    for quote_div in soup.find_all("div", class_="quote"):
        text = quote_div.find("span", class_="text").text
        author = quote_div.find("small", class_="author").text
        tags = [tag.text for tag in quote_div.find_all("a", class_="tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))
    return quotes


def main(output_csv_path: str) -> None:
    all_quotes = []

    page_number = 1
    while True:
        page_url = f"{BASE_URL}/page/{page_number}/"
        page_content = fetch_page(page_url)
        if page_content is None:
            break

        quotes = parse_quotes(page_content)
        all_quotes.extend(quotes)

        soup = BeautifulSoup(page_content, "html.parser")
        next_button = soup.find("li", class_="next")
        if not next_button:
            break

        page_number += 1

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for quote in all_quotes:
            writer.writerow(quote.__dict__)


if __name__ == "__main__":
    main("quotes.csv")
