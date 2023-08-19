import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select("a.tag")],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_page_url(page_num: int) -> bytes:
    return requests.get(f"{BASE_URL}page/{page_num}/").content


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    page_num = 1

    while True:
        page = get_page_url(page_num)
        soup = BeautifulSoup(page, "html.parser")
        quotes = get_single_page_quotes(soup)

        if not quotes:
            break

        all_quotes.extend(quotes)
        page_num += 1

    return all_quotes


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def write_quotes_to_csv(quotes: [Quote], csv_file: str) -> None:
    with open(csv_file, "w", encoding="utf-8", newline="") as output_csv_file:
        writer = csv.writer(output_csv_file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes=quotes, csv_file=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
