import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup, Tag
from tqdm import tqdm


BASE_URL = "https://quotes.toscrape.com/"

QUOTES_OUTPUT_CSV_PATH = "quotes.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[
            tag.text for tag in quote_soup.select(".tag")
        ]
    )


def get_single_page_quotes(page_soup: Tag) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [
        parse_single_quote(quote) for quote in quotes
    ]


def get_all_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")
    all_quotes = get_single_page_quotes(first_page_soup)

    for page_number in tqdm(range(2, 11)):
        page = requests.get(f"{BASE_URL}/page/{page_number}/").content
        page_soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(page_soup))

    return all_quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main(QUOTES_OUTPUT_CSV_PATH)
