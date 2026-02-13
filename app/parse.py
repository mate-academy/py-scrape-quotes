import time
import csv
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_quotes(soup: BeautifulSoup) -> list[Quote]:
    quotes = []

    quote_blocks = soup.find_all("div", class_="quote")

    for block in quote_blocks:
        text = block.find("span", class_="text").get_text(strip=True)
        author = block.find("small", class_="author").get_text(strip=True)
        tags = [tag.get_text(strip=True)
                for tag in block.find_all("a", class_="tag")]

        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def get_next_page(soup: BeautifulSoup) -> str | None:
    next_button = soup.find("li", class_="next")

    if next_button:
        relative_url = next_button.find("a")["href"]
        return urljoin(BASE_URL, relative_url)
    return None


def main(output_csv_path: str) -> None:
    url = BASE_URL
    all_quotes = []

    while url:
        soup = fetch_page(url)
        quotes = parse_quotes(soup)
        all_quotes.extend(quotes)
        url = get_next_page(soup)
        time.sleep(0.5)

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(["text", "author", "tags"])

        for quote in all_quotes:
            writer.writerow([
                quote.text,
                quote.author,
                str(quote.tags)
            ])


if __name__ == "__main__":
    main("quotes.csv")
