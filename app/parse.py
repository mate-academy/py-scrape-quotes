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


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_page_soup(session: requests.Session, url: str) -> BeautifulSoup:
    response = session.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def get_all_quotes() -> list[Quote]:
    quotes = []
    url = BASE_URL
    with requests.Session() as session:
        while url:
            soup = get_page_soup(session, url)
            quotes.extend(
                parse_single_quote(quote_soup)
                for quote_soup in soup.select(".quote")
            )
            next_link = soup.select_one("li.next > a")
            url = urljoin(BASE_URL, next_link["href"]) if next_link else None
    return quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
