import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

QUOTES_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_single_quote(quote: BeautifulSoup) -> Quote:
    tags = [tag.text for tag in quote.select(".tag")]
    return (Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=tags,
    ))


def get_single_page_quotes(page_soup: Tag) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [get_single_quote(quote) for quote in quotes]


def get_quotes() -> [Quote]:
    quotes = []
    url = QUOTES_URL

    while url:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        quotes.extend(get_single_page_quotes(soup))

        next_button = soup.select_one(".next a")
        if next_button:
            url = urljoin(QUOTES_URL, next_button["href"])
        else:
            url = None

    return quotes


def write_quotes_to_csv(quotes: [Quote], filename: str) -> None:
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
