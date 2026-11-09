import csv
from dataclasses import dataclass, fields, astuple
import requests
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"
HOME_URL = urljoin(BASE_URL, "/")


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_page_quotes(url: str) -> tuple[list[Quote], str | None]:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    quotes = [parse_single_quote(item) for item in soup.select(".quote")]

    next_link = soup.select_one("li.next a")
    next_url = urljoin(url, next_link["href"]) if next_link else None

    return quotes, next_url


def write_quotes_to_csv(path: str, quotes: list[Quote]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)

        for quote in quotes:
            row = (quote.text, quote.author, ", ".join(quote.tags))
            writer.writerow(row)


def main(output_csv_path: str) -> None:
    url = HOME_URL
    quotes = []

    while url:
        page_quotes, url = get_page_quotes(url)
        quotes.extend(page_quotes)

    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
