import csv
import requests

from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Generator
from tqdm import tqdm

URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def page_generator(url: str) -> Generator[bytes, None, None]:
    page_num = 1
    while True:
        response = requests.get(f"{url}/page/{page_num}/")

        if response.status_code != 200:
            break

        yield response.content
        page_num += 1


def parse_quotes(page_content: bytes) -> list[Quote]:
    soup = BeautifulSoup(page_content, "html.parser")
    quotes = []

    for quote_item in soup.select("div.quote"):
        text = quote_item.select_one("span.text").text.strip()
        author = quote_item.select_one("small.author").text.strip()
        tags = [tag.text for tag in quote_item.select("div.tags a.tag")]

        quotes.append(Quote(text, author, tags))

    return quotes


def scrape_quotes(base_url: str) -> list[Quote]:
    quotes = []

    for page in tqdm(page_generator(base_url), desc="Fetching quotes"):
        quotes.extend(parse_quotes(page))

    return quotes


def write_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Text", "Author", "Tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, ", ".join(quote.tags)])


def main(output_csv_path: str) -> None:
    print("Starting to scrape quotes...")
    quotes = scrape_quotes(URL)
    print(f"Scraped {len(quotes)} quotes.")
    write_to_csv(quotes, output_csv_path)
    print(f"Quotes saved to '{output_csv_path}'.")


if __name__ == "__main__":
    main("quotes.csv")
