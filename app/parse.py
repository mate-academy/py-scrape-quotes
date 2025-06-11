import csv
from dataclasses import dataclass
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import Generator
from tqdm import tqdm
import requests

URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page_content(url: str) -> bytes | None:
    """Fetch page content."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None


def page_generator(base_url: str) -> Generator[BeautifulSoup, None, None]:
    """Yield pages."""
    page_counter = 1
    while True:
        page_url = urljoin(base_url, f"page/{page_counter}/")
        content = fetch_page_content(page_url)
        if not content:
            break

        soup = BeautifulSoup(content, "lxml")
        if not soup.select(".quote"):
            break

        yield soup
        page_counter += 1


def parse_page(page: BeautifulSoup) -> list[Quote]:
    """Parse quotes from page."""
    quotes = []
    for quote_html in page.select(".quote"):
        author = quote_html.select_one(".author").text.strip()
        text = quote_html.select_one(".text").text.strip()
        tags = [tag.text for tag in quote_html.select(".tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))
    return quotes


def get_all_quotes() -> list[Quote]:
    """Get all quotes."""
    all_quotes = []
    for page in tqdm(page_generator(URL), desc="Scraping pages"):
        all_quotes.extend(parse_page(page))
    return all_quotes


def export_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    """Save quotes to CSV."""
    with open(output_csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            tags_str = str(quote.tags).replace('"', "'")
            writer.writerow([quote.text, quote.author, tags_str])


def main(output_csv_path: str) -> None:
    """Main entry."""
    quotes = get_all_quotes()
    export_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
