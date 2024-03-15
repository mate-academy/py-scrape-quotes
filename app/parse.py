import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"
PAGE_URL = BASE_URL + "page/{page_number}"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_single_page_quotes(quote_soup: BeautifulSoup) -> [Quote]:
    quotes = quote_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(soup)
    num_page = 2
    while soup.select_one(".next") is not None:
        page = requests.get(PAGE_URL.format(page_number=num_page)).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        num_page += 1

    return all_quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8",) as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
