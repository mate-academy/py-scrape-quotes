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
        logging.FileHandler("parse.log"),
        logging.StreamHandler(sys.stdout),
    ]
)


def get_single_quote(quote: Tag) -> Quote:
    return Quote(
        quote.select_one(".text").text,
        quote.select_one(".author").text,
        [tag.text for tag in quote.select(".tags .tag")],
    )


def get_single_page_quotes(page_num: int) -> [Quote]:
    paginate_url = urljoin(BASE_URL, f"page/{page_num}/")
    text = requests.get(paginate_url).content
    soup = BeautifulSoup(text, "html.parser")
    quotes = soup.select(".quote")
    return quotes


def parse_quotes() -> [Quote]:
    page_num = 1
    logging.info(f"Start parsing page {page_num}")
    all_quotes = get_single_page_quotes(page_num)
    while True:
        page_num += 1
        logging.info(f"Start parsing page {page_num}")
        quotes = get_single_page_quotes(page_num)
        if not quotes:
            break
        else:
            all_quotes += quotes
    return [get_single_quote(quote) for quote in all_quotes]


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = parse_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
