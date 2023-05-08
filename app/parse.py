import csv
from dataclasses import dataclass, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


HOME_URL = "https://quotes.toscrape.com/"


def get_one_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags a")],
    )


def get_quotes_from_page(page_soup: BeautifulSoup) -> list:
    quotes = page_soup.select(".quote")
    return [get_one_quote(quote) for quote in quotes]


def get_all_quotes() -> list:
    all_quotes = []
    for page_num in range(1, 11):
        page_url = urljoin(HOME_URL, f"/page/{page_num}/")
        page = requests.get(page_url).content
        page_soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_quotes_from_page(page_soup))
    return all_quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        for quote in get_all_quotes():
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
