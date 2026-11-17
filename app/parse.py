import csv
from dataclasses import astuple, dataclass, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"
REQUEST_TIMEOUT = 10


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
    response = session.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def get_next_page_url(page_soup: BeautifulSoup) -> str | None:
    next_link = page_soup.select_one("li.next > a")
    if next_link is None:
        return None
    return urljoin(BASE_URL, next_link["href"])


def get_all_quotes() -> list[Quote]:
    quotes = []
    page_url = BASE_URL

    with requests.Session() as session:
        while page_url:
            page_soup = get_page_soup(session, page_url)
            quotes.extend(
                parse_single_quote(quote_soup)
                for quote_soup in page_soup.select(".quote")
            )
            page_url = get_next_page_url(page_soup)

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
