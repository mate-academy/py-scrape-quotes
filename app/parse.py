import csv
from dataclasses import dataclass, fields, asdict
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    @staticmethod
    def quote_fields() -> list[str]:
        return [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def parse_single_page(soup_page: BeautifulSoup) -> List[Quote]:
    quotes = soup_page.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quote() -> List[Quote]:
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")
    all_quotes = parse_single_page(first_page_soup)

    if first_page_soup.select("li.next"):
        page_num = 2

        while True:
            next_page = requests.get(
                urljoin(BASE_URL, f"page/{page_num}/")
            ).content
            next_page_soup = BeautifulSoup(next_page, "html.parser")
            all_quotes.extend(parse_single_page(next_page_soup))

            if not next_page_soup.select("li.next"):
                break

            page_num += 1

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quote()
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=Quote.quote_fields())

        writer.writeheader()

        for quote in quotes:
            writer.writerow(asdict(quote))


if __name__ == "__main__":
    main("quotes.csv")
