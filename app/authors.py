import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"

AUTHORS = {}


@dataclass
class Author:
    name: str
    born_date: str
    born_location: str
    biography: str


def get_author_soup(soup: BeautifulSoup) -> BeautifulSoup:
    author_bio_path = soup.select_one("a")["href"]
    author_bio_page = requests.get(
        BASE_URL + author_bio_path
    ).content
    author_bio_soup = BeautifulSoup(author_bio_page, "html.parser")

    return author_bio_soup


def get_author_instance(soup: BeautifulSoup) -> Author:
    author = Author(
        name=soup.select_one(".author-title").text.replace("-", " "),
        born_date=soup.select_one(".author-born-date").text,
        born_location=soup.select_one(".author-born-location").text,
        biography=soup.select_one(".author-description").text.strip()
    )
    AUTHORS[author.name] = author

    return author


def get_author(soup: BeautifulSoup) -> Author:
    author_name = soup.select_one(".author").text
    if author_name in AUTHORS:
        return AUTHORS.get(author_name)
    else:
        author_soup = get_author_soup(soup)
        return get_author_instance(author_soup)


def create_authors_csv_file() -> None:
    with open(
            "authors.csv",
            "w",
            newline="",
            encoding="utf-8"
    ) as csvfile:
        fieldnames = [
            "name",
            "born date",
            "born location",
            "biography",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for author in AUTHORS.values():
            writer.writerow({
                "name": author.name,
                "born date": author.born_date,
                "born location": author.born_location[3:],
                "biography": author.biography,
            })
