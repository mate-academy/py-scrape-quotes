import csv
from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://quotes.toscrape.com/"
QUOTES_OUTPUT_CSV_PATH = "quotes.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


HEADERS_OF_FILE = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup):
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=list(
            quote_soup.select_one(
                ".keywords"
            )["content"].replace(",", " ").split()
        )
    )


def parse_single_page_quotes(quotes_soup: BeautifulSoup):
    quotes = quotes_soup.select(".quote")

    return [parse_single_quote(quote) for quote in quotes]


def parse_all_quotes():
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    all_quotes = parse_single_page_quotes(soup)
    page_num = 2

    while True:
        page = requests.get(f"{BASE_URL}/page/{page_num}/").content
        soup = BeautifulSoup(page, "html.parser")

        all_quotes.extend(parse_single_page_quotes(soup))

        if soup.select_one("li.next") is None:
            break

        page_num += 1
    return all_quotes


def write_quotes_to_csv(quotes: [Quote], path_to_file: str):
    with open(path_to_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(HEADERS_OF_FILE)
        writer.writerows(quotes)


def main(output_csv_path: str) -> None:
    quotes = parse_all_quotes()
    write_quotes_to_csv([astuple(quote) for quote in quotes], output_csv_path)


if __name__ == "__main__":
    main(QUOTES_OUTPUT_CSV_PATH)
