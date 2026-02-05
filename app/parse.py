from dataclasses import dataclass, fields, astuple
import csv
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from packaging.tags import Tag
from requests import get


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [
    field.name for field in fields(Quote)
]


URL = "https://quotes.toscrape.com/"


def parse_quote(quote: Tag) -> Quote:
    tags = quote.select_one(".tags .keywords")["content"]

    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=tags.split(",") if tags else []
    )


def get_quotes_from_one_page(soup: BeautifulSoup) -> list[Quote]:
    quotes = soup.select(selector=".quote")
    return [
        parse_quote(quote)
        for quote in quotes
    ]


def get_soup(url: str) -> BeautifulSoup:
    response = get(url)
    return BeautifulSoup(response.content, "html.parser")


def scrape_all_quotes(start_url: str) -> list[Quote]:
    current_url = start_url
    result_list = []

    while current_url:
        soup = get_soup(url=current_url)

        result_list.extend(
            get_quotes_from_one_page(soup=soup)
        )

        next_btn = soup.select_one("li.next a")

        if next_btn:
            relative_link = next_btn["href"]
            current_url = urljoin(start_url, relative_link)
        else:
            current_url = None

    return result_list


def write_to_csv_file(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w") as destination_file:
        writer = csv.writer(destination_file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_to_csv_file(
        output_csv_path,
        scrape_all_quotes(start_url=URL)
    )


if __name__ == "__main__":
    main("quotes.csv")
