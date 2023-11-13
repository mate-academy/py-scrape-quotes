import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"
QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one("span.text").text,
        author=quote.select_one("small.author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def get_quotes() -> [Quote]:
    quotes = []
    page_num = 1

    while True:
        curr_url = urljoin(BASE_URL, f"/page/{page_num}/")
        page = requests.get(curr_url).content
        soup = BeautifulSoup(page, "html.parser")
        page_quotes = soup.select(".quote")
        quotes.extend([parse_single_quote(quote) for quote in page_quotes])
        if not soup.select("li.next"):
            break
        page_num += 1

    return quotes


def write_quotes_to_csv(output_csv_path: str, quotes: [Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
