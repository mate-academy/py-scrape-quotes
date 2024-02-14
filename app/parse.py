import csv
from dataclasses import dataclass, astuple, fields
from typing import Type
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    born_date: str
    born_location: str
    description: str


authors_of_quotes = []


def get_fields_name(instance: Type[Quote | Author]) -> list[str]:
    return [field.name for field in fields(instance)]


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one("span.text").text,
        author=quote_soup.select_one("small.author").text,
        tags=quote_soup.select_one("div.tags").text.split()[1:],
    )


def parse_single_author(quote_soup: Tag) -> Author:
    author_url = quote_soup.select_one(".quote a")["href"]
    author_page = requests.get(BASE_URL + author_url).content
    author_soup = BeautifulSoup(author_page, "html.parser")
    author_name = author_soup.select_one(".author-title").text
    authors_of_quotes.append(author_name)

    return Author(
        name=author_name,
        born_date=author_soup.select_one(".author-born-date").text,
        born_location=author_soup.select_one(".author-born-location").text,
        description=author_soup.select_one(".author-description").text,
    )


def parse_quotes(soup: BeautifulSoup) -> [Quote]:
    quotes = soup.select("div.quote")

    return [parse_single_quote(quote) for quote in quotes]


def parse_authors(soup: BeautifulSoup) -> [Author]:
    quotes = soup.select("div.quote")

    return [
        parse_single_author(quote)
        for quote in quotes
        if quote.select_one("small.author").text
        not in authors_of_quotes
    ]


def write_data_to_csv(
        csv_file: str,
        instance_fields: list,
        instances: list[Quote] | list[Author]
) -> None:
    with open(csv_file, "a") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(instance_fields)
        writer.writerows([astuple(instance) for instance in instances])


def main(output_csv_path: str) -> None:
    actual_url = BASE_URL
    quotes = []
    authors = []

    while True:
        page = requests.get(actual_url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(parse_quotes(soup))
        authors.extend(parse_authors(soup))
        next_page = soup.select_one(".next a")

        if not next_page:
            break
        actual_url = urljoin(BASE_URL, next_page["href"])

    quote_fields = get_fields_name(Quote)
    author_fields = get_fields_name(Author)

    write_data_to_csv(output_csv_path, quote_fields, quotes)
    write_data_to_csv("authors_of_quotes.csv", author_fields, authors)


if __name__ == "__main__":
    main("quotes.csv")
