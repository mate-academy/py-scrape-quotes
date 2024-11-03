import csv
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


def parse_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").get_text(strip=True)
    author = quote_soup.select_one(".author").get_text(strip=True)
    tags = [tag.get_text(strip=True) for tag in quote_soup.select(".tag")]
    return Quote(text, author, tags)


def get_all_quotes() -> List[Quote]:
    quotes = []
    page_num = 1

    while True:
        response = requests.get(f"{BASE_URL}/page/{page_num}")
        soup = BeautifulSoup(response.content, "html.parser")

        quote_blocks = soup.select(".quote")
        if not quote_blocks:
            break
        for quote_block in quote_blocks:
            quote = parse_quote(quote_block)
            quotes.append(quote)

        next_button = soup.select_one(".next > a")
        if not next_button:
            break
        page_num += 1

    return quotes


def save_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Text", "Author", "Tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, ", ".join(quote.tags)])


def main(output_quotes_csv: str) -> None:

    quotes = get_all_quotes()

    save_quotes_to_csv(quotes, output_quotes_csv)


if __name__ == "__main__":
    main("quotes.csv")
