import csv
import logging
import re
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

URL = "https://quotes.toscrape.com/"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    tags = quote_soup.select(".tags > a.tag")

    return Quote(
        text=quote_soup.select_one(".quote > span.text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in tags]
    )


def get_single_page(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_pages_number(page_soup: BeautifulSoup) -> int:
    number_of_page = 0
    while True:
        is_next = page_soup.select_one(".pager > li[class*='next']")
        if is_next:
            next_page = page_soup.select_one(
                ".pager > .next > a[href*='page']"
            ).get("href")

            url = urljoin(URL, next_page)
            number_of_page = re.findall(r"\b\d+", next_page)[0]
            logging.info(f"Pages counting... #{number_of_page}....{url}")

            page = requests.get(url).content
            page_soup = BeautifulSoup(page, "html.parser")

            number_of_page = int(number_of_page) - 1
            number_of_page += 1

        else:
            break

    return number_of_page


def get_all_quotes() -> [Quote]:
    page = requests.get(URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page(first_page_soup)
    num_page = get_pages_number(first_page_soup)

    for num in range(2, num_page + 1):
        logging.info(f"Parsing page #{num}...")

        next_page_url = urljoin(URL, f"/page/{num}/")
        next_page = requests.get(next_page_url).content
        current_page_soup = BeautifulSoup(next_page, "html.parser")

        all_quotes.extend(get_single_page(current_page_soup))

    return all_quotes


def wright_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    wright_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
