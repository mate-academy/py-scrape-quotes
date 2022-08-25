import csv

from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

from app.author import write_authors_to_csv, get_authors_list

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_tags_for_single_quote(tags: BeautifulSoup) -> list:
    return [tag.text for tag in tags]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=parse_tags_for_single_quote(quote.select(".tags > a")),
    )


def get_single_page_quotes(soup: BeautifulSoup) -> [Quote]:
    quotes = soup.select(".quote")

    return [parse_single_quote(quote) for quote in quotes]


def get_all_page_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(soup)
    number_page = 2

    while True:
        page = requests.get(f"{BASE_URL}/page/{number_page}").content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        number_page += 1

        if soup.select_one("li.next") is None:
            break

    return all_quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="",) as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_page_quotes()
    authors = get_authors_list(
        set([quote.author for quote in quotes])
    )

    write_quotes_to_csv(quotes, output_csv_path)
    write_authors_to_csv(authors)


if __name__ == "__main__":
    main("quotes.csv")
