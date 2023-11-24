import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"

QUOTES_OUTPUT_CSV_PATH = "../output_data/quotes.csv"
BIOGRAPHIES_OUTPUT_CSV_PATH = "../output_data/biographies.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Biography:
    author: str
    born_date: str
    born_location: str
    description: str


QUOTE_FIELDS = [field.name for field in fields(Quote)]
BIOGRAPHY_FIELDS = [field.name for field in fields(Biography)]

links_about_authors = {}


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    author = quote_soup.select_one(".author").text

    if author not in links_about_authors:
        links_about_authors[author] = quote_soup.select_one("a[href]")["href"]

    return Quote(
        text=quote_soup.select_one(".text").text,
        author=author,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(soup)

    while soup.select_one(".next"):
        next_page = soup.select_one(".next > a[href]")["href"]
        next_url = urljoin(BASE_URL, next_page[1:])
        page = requests.get(next_url).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))

    return all_quotes


def parse_single_biography(biography_soup: BeautifulSoup) -> Biography:
    return Biography(
        author=biography_soup.select_one(".author-title").text,
        born_date=biography_soup.select_one(".author-born-date").text,
        born_location=biography_soup.select_one(".author-born-location").text,
        description=biography_soup.select_one(".author-description").text,
    )


def get_biographies() -> [Biography]:
    all_biographies = []

    for link in links_about_authors.values():
        url = urljoin(BASE_URL, link[1:])
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        all_biographies.append(parse_single_biography(soup))

    return all_biographies


def write_items_to_csv(
    items: [Quote | Biography],
    items_output_csv_path: str,
    item_fields: [str],
) -> None:
    with open(
        items_output_csv_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(item_fields)
        writer.writerows([astuple(item) for item in items])


def main() -> None:
    quotes = get_quotes()
    write_items_to_csv(
        items=quotes,
        items_output_csv_path=QUOTES_OUTPUT_CSV_PATH,
        item_fields=QUOTE_FIELDS,
    )
    biographies = get_biographies()
    write_items_to_csv(
        items=biographies,
        items_output_csv_path=BIOGRAPHIES_OUTPUT_CSV_PATH,
        item_fields=BIOGRAPHY_FIELDS,
    )


if __name__ == "__main__":
    main()
