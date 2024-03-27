import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dataclasses import astuple

from .parse_quotes import (
    Quote,
    get_quotes_from_page,
    QUOTE_FIELDS
)
from .parse_authors import (
    get_authors_from_page,
    AUTHORS_FIELDS,
)
from .helper import BASE_QUOTES_URL


QUOTES_CSV = "result.csv"
AUTHORS_CSV = "authors.csv"


def next_quote_page_exist(soup: BeautifulSoup) -> BeautifulSoup:
    return soup.select_one("li.next > a")


def write_in_cvs_file(
        column_fields: [str],
        data: [Quote],
        csv_file: str
) -> None:
    with open(csv_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(column_fields)
        writer.writerows([astuple(record) for record in data])


def main(output_csv_path: str) -> None:
    """ Scrape quotes and authors of quote """
    page_num = 1
    while True:
        page = requests.get(
            urljoin(BASE_QUOTES_URL, f"page/{page_num}/")
        ).content
        page_soup = BeautifulSoup(page, "html.parser")

        # first parse quotes
        quotes = get_quotes_from_page(page_soup)
        # and quotes author info
        authors = get_authors_from_page(page_soup)

        # verify if next page exist
        if not next_quote_page_exist(page_soup):
            break
        page_num += 1

    write_in_cvs_file(AUTHORS_FIELDS, authors, AUTHORS_CSV)
    write_in_cvs_file(QUOTE_FIELDS, quotes, output_csv_path)


if __name__ == "__main__":
    main(QUOTES_CSV)
