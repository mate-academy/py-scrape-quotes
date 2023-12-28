import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


@dataclass
class Biography:
    author: str
    born: str
    description: str


BIOGRAPHY_FIELDS = [field.name for field in fields(Biography)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags > .tag")]
    )


def parse_single_author(quote_soup: BeautifulSoup) -> Biography:
    return Biography(
        author=quote_soup.select_one(".author-title").text,
        born=quote_soup.select_one(".author-born-location").text,
        description=quote_soup.select_one(".author-description").text
    )


def get_biography(author_names: [str]) -> [Biography]:
    all_biography = []
    for author in author_names:
        author = "author/" + author
        author = (
            author.replace(". ", "-")
            .replace(".", "-")
            .replace(" ", "-")
            .replace("'", "")
        )

        page = requests.get(urljoin(BASE_URL, author)).content
        soup = BeautifulSoup(page, "html.parser")
        authors = soup.select(".author-details")
        all_biography.extend(
            [parse_single_author(parse_author) for parse_author in authors]
        )

    return all_biography


def get_quotes() -> [Quote]:
    num_page = 0
    all_quotes = []
    while True:
        num_page += 1

        page = requests.get(urljoin(BASE_URL, f"page/{num_page}")).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = soup.select(".quote")

        if len(quotes) == 0:
            return all_quotes

        all_quotes.extend(
            [parse_single_quote(parse_quote) for parse_quote in quotes]
        )


def write_quotes_to_csv(output_csv_path: str, quotes: [Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_bio_to_csv(output_csv_path: str, biography: [Biography]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(BIOGRAPHY_FIELDS)
        writer.writerows([astuple(bio) for bio in biography])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    authors = [authors.author for authors in quotes]
    biography = get_biography(authors)
    write_quotes_to_csv(output_csv_path, quotes)
    write_bio_to_csv("bio.csv", biography)


if __name__ == "__main__":
    main("quotes.csv")
