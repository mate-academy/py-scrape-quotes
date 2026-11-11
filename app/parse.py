import csv
import time
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_page(html: str) -> tuple[list[Quote], str | None]:
    soup = BeautifulSoup(html, "html.parser")
    quotes = []

    for quote_div in soup.select(".quote"):
        text = quote_div.select_one(".text").get_text(strip=True)
        author = quote_div.select_one(".author").get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag in quote_div.select(".tag")]

        quotes.append(Quote(text=text, author=author, tags=tags))

    next_btn = soup.select_one(".pager .next a")
    next_page_url = next_btn["href"] if next_btn else None

    return quotes, next_page_url


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    current_url = BASE_URL

    while current_url:
        response = requests.get(current_url)
        response.raise_for_status()

        page_quotes, next_page = parse_single_page(response.text)
        all_quotes.extend(page_quotes)

        if next_page:
            current_url = f"{BASE_URL}{next_page}"
            time.sleep(1)
        else:
            current_url = None

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, ", ".join(quote.tags)])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
