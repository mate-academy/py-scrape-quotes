import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"
HOME_URL = urljoin(BASE_URL, "page/")


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=list(map(lambda tag: tag.text, quote.select(".tag")))
    )


def get_all_quotes_on_page(page_url: str) -> [Quote]:
    text = requests.get(page_url).content
    soup = BeautifulSoup(text, "html.parser")
    all_quotes = soup.select(".quote")
    quotes = [parse_single_quote(quote) for quote in all_quotes]
    return quotes


def main(output_csv_path: str) -> None:
    current_page_number = 1
    quotes = []
    result_of_parse = get_all_quotes_on_page(urljoin(
        HOME_URL,
        str(current_page_number)
    ))
    while result_of_parse:
        quotes.extend(result_of_parse)
        current_page_number += 1
        result_of_parse = get_all_quotes_on_page(urljoin(
            HOME_URL,
            str(current_page_number)
        ))

    with open(f"{output_csv_path}", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
