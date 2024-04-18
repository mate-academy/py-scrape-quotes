import csv
import logging
import sys
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


def parse_single_quote(quote_soup: Tag) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = [tag.text for tag in quote_soup.select(".tag")]
    return Quote(
        text=text,
        author=author,
        tags=tags
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select("div.quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes_data() -> list[Quote]:
    logging.info("Start parsing page 1")
    response = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(response, "html.parser")

    next_page = (first_page_soup.select_one("div.row"
                                            " > div.col-md-8"
                                            " > nav"
                                            " > ul"
                                            " > li.next"))

    all_quotes = get_single_page_quotes(first_page_soup)

    page_number = 2
    while next_page:
        logging.info(f"Start parsing page {page_number}")
        response = requests.get(f"{BASE_URL}page/{page_number}/").content
        soup = BeautifulSoup(response, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        next_page = soup.select_one("div.row"
                                    " > div.col-md-8"
                                    " > nav"
                                    " > ul"
                                    " > li.next"
                                    )
        page_number += 1

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes_data()
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(quotes[0].__annotations__.keys())
        for instance in quotes:
            writer.writerow(instance.__dict__.values())


if __name__ == "__main__":
    main("quotes.csv")
