from dataclasses import dataclass
from urllib.parse import urljoin
import csv
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


def get_quotes_per_page(soup: BeautifulSoup) -> list[Quote]:
    quotes = soup.select(".quote")
    return [get_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    url = BASE_URL

    while True:
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = get_quotes_per_page(soup)
        all_quotes.extend(quotes)
        next_button = soup.select_one("ul.pager li.next a")
        if next_button is None:
            break
        url = urljoin(BASE_URL, next_button["href"])

    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("text", "author", "tags"))
        for quoter in quotes:
            writer.writerow((quoter.text, quoter.author, quoter.tags))


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
