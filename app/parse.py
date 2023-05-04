import csv
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_quotes_on_page(url: str) -> list[Quote]:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    quotes_on_page = [
        Quote(
            text=quote_block.select_one(".text").text,
            author=quote_block.select_one(".author").text,
            tags=[tag.text for tag in quote_block.select(".tag")],
        )
        for quote_block in soup.select(".quote")
    ]
    return quotes_on_page


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    url = BASE_URL
    while url:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        all_quotes.extend(get_quotes_on_page(url))
        next_page_link = soup.select_one(".next > a")
        url = BASE_URL + next_page_link["href"] if next_page_link else None
    return all_quotes


def save_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    save_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
