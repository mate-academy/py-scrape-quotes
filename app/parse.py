from dataclasses import dataclass, astuple, fields
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Biography:
    author: str
    bio: str


BASE_URL = "https://quotes.toscrape.com/"

QOUTES_OUTPUT_CSV_PATH = "quotes.csv"

QUOTE_FIELDS = [field.name for field in fields(Quote)]

BIO_OUTPUT_CSV_PATH = "biography.csv"

BIO_FIELDS = [field.name for field in fields(Biography)]

AUTHORS = {}


def write_quotes_to_csv(quotes: [Quote], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_bio_to_csv(biography: [Biography], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(BIO_FIELDS)
        writer.writerows([astuple(bio) for bio in biography])


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    quote_tags = []
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = quote_soup.select(".tags > .tag")

    if tags:
        quote_tags = [tag.text for tag in tags]

    if author not in AUTHORS:
        AUTHORS.update(
            {
                author: quote_soup.select_one(".author + a")["href"]
            }
        )

    return Quote(
        text=text,
        author=author,
        tags=quote_tags,
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> [Quote]:
    all_quotes = []
    page_number = 1

    while True:
        page = requests.get(urljoin(BASE_URL, f"page/{page_number}/")).content
        soup = BeautifulSoup(page, "html.parser")

        if not soup.select(".quote"):
            break

        all_quotes.extend(get_single_page_quotes(soup))

        page_number += 1

    return all_quotes


def parse_single_bio(bio_soup: BeautifulSoup) -> Biography:

    return Biography(
        author=bio_soup.select_one(".author-title").text,
        bio=bio_soup.select_one(".author-description").text,
    )


def get_biography() -> [Biography]:
    all_bios = []

    for author, url in AUTHORS.items():
        page = requests.get(urljoin(BASE_URL, url)).content
        soup = BeautifulSoup(page, "html.parser")

        all_bios.append(parse_single_bio(soup))

    return all_bios


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)
    bio = get_biography()
    write_bio_to_csv(bio, BIO_OUTPUT_CSV_PATH)


if __name__ == "__main__":
    main(QOUTES_OUTPUT_CSV_PATH)
