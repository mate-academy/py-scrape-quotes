import csv
from dataclasses import dataclass, astuple
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"
QUOTE_FIELDS = ["text", "author", "tags"]
QUOTES_OUTPUT_CSV_PATH = "all_quotes.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_next_page_url(soup: BeautifulSoup) -> str:
    next_page = soup.select_one(".next a")
    if next_page:
        return BASE_URL + next_page["href"]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_quotes() -> list[Quote]:
    quotes = []
    next_page_url = BASE_URL

    while next_page_url:
        page = requests.get(next_page_url)
        soup = BeautifulSoup(page.content, "html.parser")
        quotes.extend(
            [
                parse_single_quote(quote_soup)
                for quote_soup in soup.select(".quote")
            ]
        )
        next_page_url = get_next_page_url(soup)

    return quotes


def write_quotes_to_csv(quotes: list[Quote]) -> None:
    with open(QUOTES_OUTPUT_CSV_PATH, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(([astuple(quote) for quote in quotes]))


if __name__ == "__main__":
    write_quotes_to_csv(get_quotes())
