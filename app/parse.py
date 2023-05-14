import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL: str = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


HOME_URL = "https://quotes.toscrape.com/"


def get_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]

    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [get_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:

    all_quotes = []

    for page_num in range(1, 11):
        page_url = urljoin(HOME_URL, f"/page/{page_num}/")
        page = requests.get(page_url).content
        page_soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(page_soup))
    return all_quotes


def get_csv_quotes(quotes: list[Quote], path: str) -> None:
    with open(path, "w") as file:
        row = csv.writer(file)
        row.writerow(QUOTE_FIELDS)
        row.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    get_csv_quotes(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
