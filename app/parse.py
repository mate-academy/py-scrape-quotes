import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def is_next_page(quote_soup: BeautifulSoup) -> bool:
    return bool(quote_soup.select(".next"))


def parse_all_quotes() -> [Quote]:
    all_quotes = []
    page_num = 1

    while True:
        page = requests.get(urljoin(BASE_URL, f"page/{page_num}")).content
        quote_soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(
            parse_single_quote(quote)
            for quote in quote_soup.find_all(class_="quote")
        )
        if not is_next_page(quote_soup):
            break
        page_num += 1

    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        for quote in quotes:
            writer.writerow(astuple(quote))


def main(output_csv_path: str) -> None:
    quotes = parse_all_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
