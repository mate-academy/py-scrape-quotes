import csv
import logging
import sys
from dataclasses import dataclass, astuple, fields
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "http://quotes.toscrape.com/"


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
    ]
)


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_num_pages(page_soup: Tag) -> Tag:
    return page_soup.select_one(".next")


def get_single_page_quotes(page_soup: Tag) -> [Quote]:
    quotes = page_soup.select("div.quote")

    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> [Quote]:
    page_num = 1
    all_quotes = []
    while True:
        logging.info(f"Start parsing quotes #{page_num}")
        text = requests.get(BASE_URL + f"page/{page_num}/").content
        page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(page_soup))
        if not get_num_pages(page_soup):
            break
        page_num += 1
    return all_quotes


def write_quotes_to_csv(quotes: [Quote], csv_name: str) -> None:
    with open(csv_name, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_all_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
