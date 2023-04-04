from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
import csv
from dataclasses import asdict


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def extract_quotes(html: str) -> list[Quote]:
    soup = BeautifulSoup(html, "html.parser")
    quote_divs = soup.find_all("div", class_="quote")
    quotes = []

    for div in quote_divs:
        text = div.find("span", class_="text").text.strip()
        author = div.find("small", class_="author").text.strip()
        tags = [a.text for a in div.find_all("a", class_="tag")]

        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def has_next_page(html: str) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    next_page = soup.find("li", class_="next")
    return next_page is not None


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com"
    page_number = 1
    all_quotes = []

    while True:
        page_url = f"{base_url}/page/{page_number}/"
        html = fetch_page(page_url)
        quotes = extract_quotes(html)
        all_quotes.extend(quotes)

        if not has_next_page(html):
            break

        page_number += 1
        print(page_number)

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for quote in all_quotes:
            writer.writerow(asdict(quote))


if __name__ == "__main__":
    main("quotes.csv")
