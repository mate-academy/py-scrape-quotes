import csv
from dataclasses import astuple, dataclass, fields
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


def parse_single_quote(quote: Tag) -> Quote:
    tags = [tag.text for tag in quote.select(".tag")]

    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=tags,
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def parse_quotes() -> list[Quote]:
    current_url = urljoin(QUOTES_URL, "/page/1/")
    all_quotes = []
    while True:
        text = requests.get(current_url).content
        page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(page_soup))

        next_page = page_soup.select_one(".next > a")
        if next_page:
            current_url = urljoin(QUOTES_URL, next_page["href"])
        else:
            break

    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = parse_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
