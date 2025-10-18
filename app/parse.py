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
        text=quote.select_one(".text").get_text(strip=True),
        author=quote.select_one(".author").get_text(strip=True),
        tags=[tag.get_text(strip=True) for tag in quote.select(".tag")],
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(q) for q in quotes]


def get_all_quotes() -> list[Quote]:
    url = BASE_URL
    all_quotes: list[Quote] = []

    while True:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")

        all_quotes.extend(get_single_page_quotes(soup))

        next_link = soup.select_one(".next a")
        if not next_link:
            break

        url = urljoin(BASE_URL, next_link["href"])

    return all_quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(q) for q in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
