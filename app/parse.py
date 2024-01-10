import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_quotes(url: str) -> list:
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    quotes = soup.select(".quote")
    return [parse_single_quote(quote_soup)
            for quote_soup in quotes]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    tags = quote_soup.select(".tag")
    tag_text = [tag.text for tag in tags]
    return Quote(text=quote_soup.select_one(".text").text,
                 author=quote_soup.select_one(".author").text,
                 tags=tag_text)


def get_all_quotes() -> list:
    all_quotes = []
    page = 1

    while True:
        url = f"{BASE_URL}/page/{page}/"
        quotes = get_quotes(url)

        if not quotes:
            break

        all_quotes.extend(quotes)
        page += 1
    return all_quotes


def write_quotes_to_csv(output_csv_path: str,
                        quotes: BeautifulSoup) -> None:
    with open(output_csv_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    all_quotes = get_all_quotes()
    write_quotes_to_csv(output_csv_path, all_quotes)


if __name__ == "__main__":
    main("quotes.csv")
