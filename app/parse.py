import csv
import time
from dataclasses import astuple, dataclass, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"
REQUEST_DELAY_SECONDS = 1


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one("span.text").text,
        author=quote_soup.select_one("small.author").text,
        tags=[tag.text for tag in quote_soup.select("a.tag")]
    )


def get_page_soup(session: requests.Session, url: str) -> BeautifulSoup:
    response = session.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_all_quotes() -> list[Quote]:
    quotes = []
    url = BASE_URL

    with requests.Session() as session:
        while url:
            page_soup = get_page_soup(session, url)
            quotes.extend(
                parse_single_quote(quote_soup)
                for quote_soup in page_soup.select("div.quote")
            )

            next_link = page_soup.select_one("li.next > a")
            url = urljoin(BASE_URL, next_link["href"]) if next_link else None

            if url:
                time.sleep(REQUEST_DELAY_SECONDS)

    return quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_all_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
