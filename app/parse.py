import csv
from dataclasses import dataclass
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


URL = "https://quotes.toscrape.com/"


def fetch_page(url: str) -> bytes:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.content


def parse_page(soup: BeautifulSoup) -> list[Quote]:
    quotes: list[Quote] = []

    for quote in soup.find_all("div", class_="quote"):
        text = quote.find("span", class_="text").get_text(strip=True)
        author = quote.find("small", class_="author").get_text(strip=True)

        tags = [
            tag.get_text(strip=True)
            for tag in quote.find_all("a", class_="tag")
        ]

        quotes.append(Quote(text, author, tags))

    return quotes


def scrape_quotes() -> list[Quote]:
    all_quotes = []
    current_url = URL

    while True:
        html = fetch_page(current_url)
        soup = BeautifulSoup(html, "html.parser")

        quotes = parse_page(soup)
        all_quotes.extend(quotes)

        next_button = soup.find("li", class_="next")

        if not next_button:
            return all_quotes

        next_href = next_button.find("a")["href"]
        current_url = urljoin(current_url, next_href)

        sleep(0.5)


def save_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(
        output_csv_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([
                quote.text,
                quote.author,
                quote.tags
            ])


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    save_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
