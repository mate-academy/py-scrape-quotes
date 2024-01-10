import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

URL = "https://quotes.toscrape.com/"
QUOTES_OUTPUT_CSV_PATH = "result.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(information_soup: BeautifulSoup) -> Quote:

    return Quote(
        text=information_soup.select_one(".text").text,
        author=information_soup.select_one(".author").text,
        tags=information_soup.select_one(".keywords")["content"].split(",")
    )


def get_single_page(page_soup: BeautifulSoup) -> [Quote]:
    information = page_soup.select(".quote")

    return [
        parse_single_quote(information_soup)
        for information_soup in information
    ]


def get_quotes() -> [Quote]:
    first_page = requests.get(URL).content
    first_page_soup = BeautifulSoup(first_page, "html.parser")
    quotes = get_single_page(first_page_soup)
    next_page = first_page_soup.select_one(".next > a")

    while next_page is not None:
        page = requests.get(urljoin(URL, next_page.get("href"))).content
        soup = BeautifulSoup(page, "html.parser")

        quotes.extend(get_single_page(soup))
        next_page = soup.select_one(".next > a")
    return quotes


def save_in_csv(information: [Quote]) -> None:
    with open(
            QUOTES_OUTPUT_CSV_PATH,
            "w",
            encoding="utf-8",
            newline=""
    ) as file:
        write = csv.writer(file)
        write.writerow(QUOTE_FIELDS)
        write.writerows([astuple(inform) for inform in information])


def main(output_csv_path: str) -> None:
    information = get_quotes()
    save_in_csv(information)


if __name__ == "__main__":
    main(QUOTES_OUTPUT_CSV_PATH)
