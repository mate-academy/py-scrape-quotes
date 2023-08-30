import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


def parse_singe_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_singe_quote(quote_soup=quote_soup) for quote_soup in quotes]


def get_quotes() -> [Quote]:
    all_quotes = []
    page_number = 1

    while True:
        url = urljoin(BASE_URL, f"page/{page_number}/")
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")

        if "No quotes found!" in soup.text:
            break

        logging.info(f"Start parsing page #{page_number}")
        all_quotes.extend(get_single_page_quotes(page_soup=soup))
        page_number += 1

    return all_quotes


def write_quotes_to_csv(quotes: [Quote], path: str) -> None:
    with open(path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes=quotes, path=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
