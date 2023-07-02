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


def parse_single_qoute(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def quotes_list() -> list[Quote]:
    value = []
    num_page = 1
    while num_page:
        url_num_page = urljoin(BASE_URL, f"page/{num_page}")
        page = requests.get(url_num_page).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = soup.select(".quote")
        if quotes:
            print(f"Start page #{num_page}")
            value.extend(
                [parse_single_qoute(quote_soup) for quote_soup in quotes]
            )
            num_page += 1
        else:
            return value


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = quotes_list()
    write_quotes_to_csv(quotes=quotes, output_csv_path=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
