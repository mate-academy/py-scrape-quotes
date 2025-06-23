from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import csv
from dataclasses import asdict, dataclass


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_quotes_from_page(url: str) -> list[Quote]:
    """Fetch quotes from a single page."""
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    quotes = []
    for quote_block in soup.select(".quote"):
        text = quote_block.select_one(".text").get_text(strip=True)
        author = quote_block.select_one(".author").get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag in quote_block.select(".tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))
    return quotes


def fetch_all_quotes(base_url: str) -> list[Quote]:
    """Fetch all quotes by navigating through pagination."""
    quotes = []
    page_url = base_url
    while page_url:
        quotes.extend(fetch_quotes_from_page(page_url))
        next_page = BeautifulSoup(
            requests.get(page_url).text,
            "html.parser"
        ).select_one(".next > a")
        page_url = urljoin(base_url, next_page["href"]) if next_page else None
    return quotes


def save_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    """Save quotes to a CSV file."""
    with open(
        output_csv_path,
        mode="w", newline="",
        encoding="utf-8"
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["text", "author", "tags"]
        )
        writer.writeheader()
        for quote in quotes:
            writer.writerow(asdict(quote))


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com/"
    quotes = fetch_all_quotes(base_url)
    save_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
