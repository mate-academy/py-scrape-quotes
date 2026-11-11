import csv
from dataclasses import astuple, dataclass, fields
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


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_all_quotes() -> list[Quote]:
    quotes = []
    next_url = BASE_URL

    while next_url:
        page = requests.get(next_url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(
            parse_single_quote(quote_soup)
            for quote_soup in soup.select(".quote")
        )
        next_link = soup.select_one(".next > a")
        next_url = (
            urljoin(BASE_URL, next_link["href"]) if next_link else None
        )

    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


if __name__ == "__main__":
    main("quotes.csv")