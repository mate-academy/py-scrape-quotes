import csv
import requests

from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.find("span", class_="text").text,
        author=quote_soup.find("small", class_="author").text,
        tags=[tag.text for tag in quote_soup.find_all("a", class_="tag")],

    )


def get_single_page_quote(quote_soup: BeautifulSoup) -> [Quote]:
    quotes = quote_soup.find_all("div", class_="quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> [Quote]:
    all_quotes = []

    current_page = 1

    while True:

        page_url = f"{BASE_URL}/page/{current_page}/"
        page = requests.get(page_url)
        next_page_url = BeautifulSoup(page.text, "html.parser")

        all_quotes.extend(get_single_page_quote(next_page_url))

        if next_page_url.select_one(".next") is None:
            break

        current_page += 1

    return all_quotes


def write_quotes_to_csv(file_name: str) -> None:
    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in get_quotes()])


def main(output_csv_path: str) -> None:
    get_quotes()

    write_quotes_to_csv(output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
