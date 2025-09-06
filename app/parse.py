import logging
import sys
from dataclasses import dataclass
from typing import List
from urllib.parse import urljoin
import csv

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"

@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("quotes.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def parse_single_quote(block: Tag) -> Quote:
    text = block.select_one(".text").get_text(strip=True)
    author = block.select_one(".author").get_text(strip=True)
    tags = [tag.get_text(strip=True) for tag in block.select(".tags .tag")]
    return Quote(text, author, tags)

def get_quotes_from_page(url: str) -> (List[Quote], str | None):
    logging.info(f"Parsing page: {url}")
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    quotes = [parse_single_quote(block) for block in soup.select(".quote")]

    next_a = soup.select_one(".pager .next a, .next a")
    next_url = urljoin(url, next_a["href"]) if next_a else None

    logging.info(f"Found {len(quotes)} quotes. Next page: {next_url}")
    return quotes, next_url

def get_all_quotes() -> List[Quote]:
    url = BASE_URL
    all_quotes: List[Quote] = []
    seen: set[str] = set()

    while url and url not in seen:
        seen.add(url)
        page_quotes, url = get_quotes_from_page(url)
        all_quotes.extend(page_quotes)

    return all_quotes

def write_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])

def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)

if __name__ == "__main__":
    main("quotes.csv")
