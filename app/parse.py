import csv
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from dataclasses import dataclass, fields, astuple


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"
QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    quote = Quote(
        text=quote_soup.select_one("span.text").text,
        author=quote_soup.select_one("span > small.author").text,
        tags=[
            tag_soup.text for tag_soup in quote_soup.select(
                "div.tags > a.tag")
        ]
    )

    return quote


def get_home_quotes() -> [Quote]:
    url_page_first = requests.get(BASE_URL).content
    soup = BeautifulSoup(url_page_first, "html.parser")
    quotes = soup.select(".quote")
    next_page = soup.select_one("nav > ul > li.next > a")["href"]
    all_quotes = [
        parse_single_quote(
            quote_soup) for quote_soup in quotes
    ]
    while next_page:
        url_next_page = urljoin(BASE_URL, next_page)
        page = requests.get(url_next_page).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = soup.select(".quote")
        if soup.select_one("nav > ul > li.next"):
            next_page = soup.select_one("nav > ul > li.next > a")["href"]
        else:
            next_page = 0

        all_quotes.extend([
            parse_single_quote(
                quote_soup) for quote_soup in quotes
        ])

    return all_quotes


def write_qoutes_to_csv(quotes: [Quote], file_out_csv: str) -> None:
    with open(file_out_csv, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    all_quotes = get_home_quotes()
    write_qoutes_to_csv(all_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
