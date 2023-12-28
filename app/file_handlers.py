import csv
from dataclasses import astuple, fields

from app.quotes_dto import Quote


def write_quotes(quotes: list[Quote], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        writer.writerows([astuple(quote) for quote in quotes])
