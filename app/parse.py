import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

QUOTES_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]:  %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    return (
        Quote(
            text=quote.select_one(".text").text,
            author=quote.select_one(".author").text,
            tags=[tag.get_text() for tag in quote.select(".tags .tag")],
        )
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> [Quote]:
    logging.info("Start parsing quotes")
    page_num = 1
    all_products = []

    while True:
        page = requests.get(
            QUOTES_URL + "/page/" + str(page_num) + "/"
        ).content
        soup = BeautifulSoup(page, "html.parser")
        all_products.extend(get_single_page_quotes(soup))
        next_page = soup.select_one(".pager > .next a")
        if next_page:
            page_num += 1
        else:
            break

    return all_products


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
