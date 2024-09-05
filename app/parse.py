import csv
from dataclasses import dataclass
from typing import Generator, List, Optional

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_html(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def extract_quote_details(quote_element: BeautifulSoup) -> Quote:
    text = quote_element.select_one(".text").get_text(strip=True)
    author = quote_element.select_one(".author").get_text(strip=True)
    tags = [tag.get_text(strip=True) for tag in quote_element.select(".tag")]
    return Quote(text=text, author=author, tags=tags)


def parse_quotes_from_page(page_soup: BeautifulSoup) -> List[Quote]:
    quote_elements = page_soup.select(".quote")
    return [extract_quote_details(quote_element)
            for quote_element in quote_elements]


def find_next_page_url(page_soup: BeautifulSoup) -> Optional[str]:
    next_button = page_soup.select_one(".next > a")
    if next_button:
        return BASE_URL + next_button["href"]
    return None


def scrape_quotes() -> Generator[Quote, None, None]:
    current_url = BASE_URL
    while current_url:
        page_soup = fetch_html(current_url)
        for quote in parse_quotes_from_page(page_soup):
            yield quote
        current_url = find_next_page_url(page_soup)


def write_quotes_to_csv(
        quotes: Generator[Quote, None, None], output_csv_path: str
) -> None:
    with open(
            output_csv_path, mode="w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
