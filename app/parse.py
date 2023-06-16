import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_next_page_url(page_soup: BeautifulSoup) -> str:
    pagination = page_soup.select_one(".next")

    if pagination is None:
        next_page_url = ""
    else:
        next_page = pagination.a["href"]
        next_page_url = urljoin(BASE_URL, next_page)

    return next_page_url


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> list[Quote]:
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(first_page_soup)
    next_page_url = get_next_page_url(first_page_soup)

    while next_page_url:
        page = requests.get(next_page_url).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        next_page_url = get_next_page_url(soup)

    return all_quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
