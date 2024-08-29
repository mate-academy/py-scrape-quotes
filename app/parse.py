from dataclasses import dataclass, asdict
import csv

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_html(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_quotes_from_page(html: str) -> list[Quote]:
    soup = BeautifulSoup(html, "html.parser")
    quotes = []
    for quote_element in soup.select(".quote"):
        text = quote_element.select_one(".text").get_text(strip=True)
        author = quote_element.select_one(".author").get_text(strip=True)
        tags = [
            tag.get_text(strip=True)
            for tag in quote_element.select(".tag")
        ]
        quotes.append(Quote(text=text, author=author, tags=tags))
    return quotes


def get_next_page_url(soup: BeautifulSoup) -> str | None:
    next_button = soup.select_one(".next > a")
    if next_button:
        return BASE_URL + next_button["href"]
    return None


def parse_all_quotes() -> list[Quote]:
    url = BASE_URL
    all_quotes = []

    while url:
        html = get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        all_quotes.extend(parse_quotes_from_page(html))
        url = get_next_page_url(soup)

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["text", "author", "tags"])
        writer.writeheader()
        for quote in quotes:
            quote_to_dict = asdict(quote)
            quote_to_dict["tags"] = str(quote_to_dict["tags"])
            writer.writerow(quote_to_dict)


def main(output_csv_path: str) -> None:
    quotes = parse_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
