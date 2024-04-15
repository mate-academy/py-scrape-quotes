import csv
from dataclasses import astuple

from bs4 import BeautifulSoup


def write_data_to_csv(
        output_csv_path: str,
        scrapped_data: list,
        field_names: list
) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(field_names)
        writer.writerows([astuple(data) for data in scrapped_data])


def next_existing_page(soup: BeautifulSoup) -> BeautifulSoup | None:
    return soup.select_one("li.next")
