import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_parse_single_qoute(qoute: Tag) -> Quote:
    tags = qoute.select_one(".keywords")["content"].split(",")
    if tags == ['']:
        tags = []
    return Quote(
        text=qoute.select_one(".text").text,
        author=qoute.select_one(".author").text,
        tags=tags
    )


def get_parse_page(qoutes_soup: list[Tag]) -> [Quote]:
    return [get_parse_single_qoute(quote) for quote in qoutes_soup]


def get_all_qoutes() -> [Quote]:
    base_url = "https://quotes.toscrape.com/"
    page_number = 1
    all_qoutes = []
    pager_soup = True
    while pager_soup is not None:
        page = requests.get(urljoin(base_url, f"/page/{page_number}")).content
        soup = BeautifulSoup(page, "html.parser")
        qoutes_soup = soup.select(".quote")
        pager_soup = soup.select_one(".next")
        all_qoutes.extend(get_parse_page(qoutes_soup))
        page_number += 1
    return all_qoutes


def main(output_csv_path: str) -> None:
    qote_field = [field.name for field in fields(Quote)]
    quotes = get_all_qoutes()
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(qote_field)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
