import csv
import time
import requests
from typing import List, Optional

from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags = [tag.text for tag in quote.select(".tag")]

    return Quote(
        text=text,
        author=author,
        tags=tags,
    )


def get_single_page_quotes(page_soup: Tag) -> List[Quote]:
    quotes = page_soup.select("div.quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_next_page_url(page_soup: Tag) -> Optional[str]:
    next_link = page_soup.select_one("li.next a")
    if not next_link:
        return None
    return BASE_URL + next_link["href"]


def get_quotes(page_url: str = BASE_URL) -> List[Quote]:
    all_quotes: List[Quote] = []
    current_page_url: Optional[str] = page_url
    while current_page_url:
        text = requests.get(current_page_url).text
        soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        current_page_url = get_next_page_url(soup)
        time.sleep(1)

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    with open(output_csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
