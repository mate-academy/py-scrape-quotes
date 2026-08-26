from dataclasses import dataclass, field
from typing import List
from bs4 import BeautifulSoup
import requests
import csv

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str] = field(default_factory=list)


def parse_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.find("span", class_="text").get_text()
    author = quote_soup.find("small", class_="author").get_text()
    tags = [tag.get_text() for tag in quote_soup.find_all("a", class_="tag")]
    return Quote(text=text, author=author, tags=tags)


def get_all_quotes() -> List[Quote]:
    quotes = []
    url = BASE_URL
    while url:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        for quote_soup in soup.find_all("div", class_="quote"):
            quotes.append(parse_quote(quote_soup))

        next_btn = soup.find("li", class_="next")
        if next_btn and next_btn.find("a"):
            url = BASE_URL.rstrip("/") + next_btn.find("a")["href"]
        else:
            url = None
    return quotes


def write_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
