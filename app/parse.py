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
        tags=[tag.text for tag in quote.select(".tag")],
    )


def parse_page(soup: BeautifulSoup) -> list[Quote]:
    return [parse_single_quote(q) for q in soup.select(".quote")]


def get_all_quotes(start_url: str) -> list[Quote]:
    url = start_url
    quotes: list[Quote] = []

    while url:
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        quotes.extend(parse_page(soup))
        nxt = soup.select_one("li.next a")
        url = urljoin(url, nxt["href"]) if nxt else None

    return quotes


def write_quotes_to_csv(quotes: list[Quote], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(q) for q in quotes)


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_all_quotes(BASE_URL), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
