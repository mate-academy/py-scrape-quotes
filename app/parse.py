import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup


QUOTES_OUTPUT_CSV_FILE = "quotes.csv"
BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.get_text() for tag in quote_soup.select(".tags > .tag")]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes_from_all_pages() -> [Quote]:
    quotes = []
    page_number = 1
    while True:
        print(f"parsing page {page_number}")
        url = (BASE_URL + f"page/{page_number}/")
        page_content = requests.get(url).content
        page_soup = BeautifulSoup(page_content, "html.parser")
        quotes.extend(get_single_page_quotes(page_soup))
        page_number += 1

        next_button = page_soup.select_one("li.next > a")
        if not next_button:
            break

    return quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes_from_all_pages()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main(QUOTES_OUTPUT_CSV_FILE)
