import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    BASE_URL = "https://quotes.toscrape.com/"
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ]
)


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_single_page_quote(quote_soup: BeautifulSoup) -> [Quote]:
    quotes = quote_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> [Quote]:
    page = requests.get(Quote.BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    all_quotes = get_single_page_quote(soup)
    next_page_tags = soup.select_one(".next")

    while next_page_tags is not None:

        next_page = next_page_tags.select_one("a")["href"]
        page = requests.get(Quote.BASE_URL + next_page)
        logging.info(f"Start parsing page {next_page_tags}")
        soup = BeautifulSoup(page.text, "html.parser")
        all_quotes.extend(get_single_page_quote(soup))
        next_page_tags = soup.select_one(".next")

    return all_quotes


def main(output_csv_path: str) -> None:

    with open(
            output_csv_path, "w", newline="", encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in get_quotes()])


if __name__ == "__main__":
    main("quotes.csv")
