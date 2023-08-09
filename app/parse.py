import csv
import logging
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

SITE_URL = "https://quotes.toscrape.com/"


logging.basicConfig(
    level=logging.INFO,
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one("span > .author").text,
        tags=[tag.text for tag in quote.select("a.tag")]
    )


def parse_one_page(soup: BeautifulSoup) -> list[Quote]:
    return [parse_quote(quote) for quote in soup.select(".quote")]


def write_data_to_csv_file(data: list[Quote], output_csv_path: str) -> str:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(QUOTES_FIELDS)

        for quote in data:
            csv_writer.writerow(astuple(quote))

    return "Data were written successfully!"


def main(output_csv_path: str) -> str:
    result = []
    num_page = 1
    while True:
        logging.info(f"Started parsing page #{num_page}")
        page = requests.get(urljoin(SITE_URL, f"page/{num_page}")).content
        soup = BeautifulSoup(page, "html.parser")
        result += parse_one_page(soup)

        if soup.select_one("li.next") is None:
            break

        num_page += 1

    write_data_to_csv_file(result, output_csv_path)
    return "Thw web site was parsed successfully!"


if __name__ == "__main__":
    main("quotes.csv")
