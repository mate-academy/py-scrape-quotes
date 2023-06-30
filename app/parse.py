import csv
from dataclasses import dataclass, astuple, fields
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


def parse_single_qoute(qoute_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=qoute_soup.select_one(".text").text,
        author=qoute_soup.select_one(".author").text,
        tags=[tag.text for tag in qoute_soup.select(".tag")],
    )


def get_list_qoute() -> [Quote]:
    value = []
    num_page = 1
    while num_page:
        url_num_page = urljoin(BASE_URL, f"page/{num_page}")
        page = requests.get(url_num_page).content
        soup = BeautifulSoup(page, "html.parser")
        qoutes = soup.select(".quote")
        if qoutes:
            print(f"Start page #{num_page}")
            value.extend(
                [parse_single_qoute(qoute_soup) for qoute_soup in qoutes]
            )
            num_page += 1
        else:
            return value


def write_qoutes_to_csv(qoutes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(qoute) for qoute in qoutes])


def main(output_csv_path: str) -> None:
    qoutes = get_list_qoute()
    write_qoutes_to_csv(qoutes=qoutes, output_csv_path=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
