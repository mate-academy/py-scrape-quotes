import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup


URL = "https://quotes.toscrape.com/"


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


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
        tags=list(tag.text for tag in quote_soup.select(".tag")),
    )


def get_num_pages() -> int:
    num_page = 1

    while True:
        page = requests.get(f"{URL}page/{num_page}/").content
        soup = BeautifulSoup(page, "html.parser")
        next_button = soup.select_one(".pager .next")

        if not next_button:
            break

        num_page += 1

    return num_page


def get_single_page_quote(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> [Quote]:
    logging.info("Start parsing page 1")
    page = requests.get(URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")
    num_pages = get_num_pages()

    all_quotes = get_single_page_quote(first_page_soup)

    for num_page in range(2, num_pages + 1):
        logging.info(f"Start parsing page {num_page}")
        page = requests.get(f"{URL}page/{num_page}/").content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quote(soup))

    return all_quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        quotes = get_all_quotes()
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
