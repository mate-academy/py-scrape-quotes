import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote):
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select("div.tags a")]
    )


def parse_quotes(url, quotes_list):
    while url:
        with requests.get(url) as response:
            soup = BeautifulSoup(response.content, "html.parser")
            for quote in soup.select(".quote"):
                yield parse_single_quote(quote)
            next_page = soup.select_one(".pager > .next > a")
            url = urljoin(BASE_URL, next_page["href"]) if next_page else None


def write_quotes_to_csv(quotes, output_csv_path, encoding="utf-8"):
    with open(output_csv_path, "w", newline='', encoding=encoding) as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = parse_quotes(BASE_URL, [])
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
