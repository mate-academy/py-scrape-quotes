import csv
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_numbeer_pages(quotes: Quote) -> int:
    count_pages = 0
    for _ in quotes:
        count_pages += 1
    return count_pages


def get_quotes_per_page(
) -> list[Quote]:
    url = requests.get(BASE_URL).content
    soup = BeautifulSoup(url, "html.parser")
    quotes = soup.select(".quote")
    number_pages = get_numbeer_pages(quotes)
    all_quotes = []
    for page_num in range(1, number_pages + 1):
        url = urljoin(BASE_URL, f"page/{page_num}/")
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = soup.select(".quote")
        quotes_per_page = [get_single_quote(quote_soup) for quote_soup in quotes]
        all_quotes.extend(quotes_per_page)
    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("text", "author", "tags"))
        for quoter in quotes:
            writer.writerow((quoter.text, quoter.author, quoter.tags))


def main(output_csv_path: str) -> None:
    quotes = get_quotes_per_page()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
