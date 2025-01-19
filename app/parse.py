import csv
import httpx

from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag

BASE_URL = "http://quotes.toscrape.com/"
NUM_PAGES = 10


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").get_text()
    author = quote.select_one(".author").get_text()
    tags = quote.select(".tags .tag")
    return Quote(text=text, author=author, tags=[tag.text for tag in tags])


def get_quotes() -> list[Quote]:
    all_quotes = []
    with httpx.Client() as client:
        for i in range(1, NUM_PAGES + 1):
            response = client.get(f"{BASE_URL}page/{i}/")
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            quotes = soup.select(".quote")
            all_quotes.extend(parse_single_quote(quote) for quote in quotes)
        return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for idx, quote in enumerate(quotes):
            writer.writerow([quote.text, quote.author, str(quote.tags)])


if __name__ == "__main__":
    main("quotes.csv")
