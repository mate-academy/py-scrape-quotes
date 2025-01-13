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


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def get_quotes(url: str) -> tuple[list[Quote], str | None]:
    content = requests.get(url).content
    soup = BeautifulSoup(content, "html.parser")

    quotes = soup.select(".quote")
    next_page_tag = soup.select_one("li.next > a")
    next_page_url = next_page_tag["href"] if next_page_tag else None

    if next_page_url:
        next_page_url = urljoin(url, next_page_url)

    return [parse_single_quote(quote) for quote in quotes], next_page_url


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    next_page_url = BASE_URL

    while next_page_url:
        quotes, next_page_url = get_quotes(next_page_url)
        all_quotes.extend(quotes)

    return all_quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_all_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
