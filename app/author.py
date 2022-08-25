import csv
from dataclasses import (
    dataclass,
    fields,
    astuple,
)

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/author"
OUTPUT_CSV_PATH = "authors.csv"


@dataclass
class Author:
    name: str
    text: str


AUTHOR_FIELDS = [field.name for field in fields(Author)]


def refactor_author_name(name: str) -> str:
    if "." in name:
        author = [i.replace(".", "-") for i in name.split()]
        return ("-".join(author)).replace("--", "-")

    return name.replace(" ", "-")


def parse_single_authors(author: str) -> Author:
    name = refactor_author_name(author)
    page = requests.get(f"{BASE_URL}/{refactor_author_name(name)}").content
    soup = BeautifulSoup(page, "html.parser")

    description = soup.select_one(".author-description").text[9:]

    return Author(name=author, text=description)


def get_authors_list(authors: set) -> [Author]:
    return [parse_single_authors(author) for author in authors]


def write_authors_to_csv(authors: [Author]) -> None:
    with open(OUTPUT_CSV_PATH, "w", newline="",) as file:
        writer = csv.writer(file)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows([astuple(author) for author in authors])
