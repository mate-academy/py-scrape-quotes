import csv
from dataclasses import astuple, fields, dataclass


@dataclass
class Author:
    lib = []
    name: str
    born_date: str
    born_location: str
    biography: str


PRODUCT_FIELDS_AUTHORS = [field.name for field in fields(Author)]


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


PRODUCT_FIELDS = [field.name for field in fields(Quote)]


def write_to_csv(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as quote:
        writer = csv.writer(quote)
        writer.writerow(PRODUCT_FIELDS)
    with open("Authors.csv", "w", encoding="utf-8", newline="") as author:
        writer = csv.writer(author)
        writer.writerow(PRODUCT_FIELDS_AUTHORS)


def save_to_csv(output_csv_path: str, all_quote: [Quote]) -> None:
    with open(output_csv_path, "a", encoding="utf-8", newline="") as quote:
        writer = csv.writer(quote)
        writer.writerows([astuple(x) for x in all_quote])


def save_authors_to_csv(output_csv_path: str, all_authors: [Author]) -> None:
    with open(output_csv_path, "a", encoding="utf-8", newline="") as author:
        writer = csv.writer(author)
        writer.writerows([astuple(author) for author in all_authors])
