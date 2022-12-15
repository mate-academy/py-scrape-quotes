import csv
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: [Tag]) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = [tag.text for tag in quote_soup.select(".tag")]

    return Quote(
        text=text,
        author=author,
        tags=tags,
    )


def get_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = soup.select(".quote")

    while soup.select_one("li.next"):
        next_page = requests.get(urljoin(
            BASE_URL, soup.select_one("li.next a")["href"]
        )).content

        soup = BeautifulSoup(next_page, "html.parser")

        all_quotes.extend(soup.select(".quote"))

    return [parse_single_quote(quote) for quote in all_quotes]


def main(output_csv_path: str) -> None:
    with open(
            output_csv_path,
            "w",
            encoding="utf-8",
            newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            [field.name for field in fields(Quote)]
        )
        writer.writerows(
            [astuple(quote) for quote in get_quotes()]
        )


if __name__ == "__main__":
    main("quotes.csv")
