import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_html: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_html.select_one(".text").text,
        author=quote_html.select_one(".author").text,
        tags=[tag.text for tag in quote_html.select(".tag")],
    )


def parse_all_quotes_on_page(url: str) -> list:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


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
