import csv
from dataclasses import astuple, dataclass, fields

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_page(soup: BeautifulSoup) -> list[Quote]:
    return [
        Quote(
            text=quote_div.select_one(".text").get_text(),
            author=quote_div.select_one(".author").get_text(),
            tags=[tag.get_text() for tag in quote_div.select(".tag")],
        )
        for quote_div in soup.select(".quote")
    ]


def get_quotes() -> list[Quote]:
    all_quotes = []
    page = 1

    with requests.Session() as session:
        while True:
            response = session.get(f"{BASE_URL}/page/{page}/", timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            all_quotes.extend(parse_page(soup))

            if not soup.select_one(".next"):
                break
            page += 1

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        for quote in quotes:
            text, author, tags = astuple(quote)
            # str() to match test fixture format
            writer.writerow([text, author, str(tags)])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
