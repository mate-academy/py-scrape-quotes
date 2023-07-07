from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import csv


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_html: BeautifulSoup) -> Quote:
    text = quote_html.find(class_="text").get_text()
    author = quote_html.find(class_="author").get_text()
    tags = [tag.get_text() for tag in quote_html.find_all(class_="tag")]
    return Quote(text=text, author=author, tags=tags)


def parse_all_quotes_on_page(url: str) -> list:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    quotes = soup.find_all(class_="quote")
    parsed_quotes = [parse_single_quote(quote) for quote in quotes]
    return parsed_quotes


def parse_quotes_from_all_pages(base_url: str) -> list:
    all_quotes = []
    page = 1
    while True:
        url = f"{base_url}page/{page}/"
        parsed_quotes = parse_all_quotes_on_page(url)
        if not parsed_quotes:
            break
        all_quotes.extend(parsed_quotes)
        page += 1
    return all_quotes


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com/"
    all_quotes = parse_quotes_from_all_pages(base_url)

    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in all_quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
