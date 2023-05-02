import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests


URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag_soup.text for tag_soup in quote_soup.select(".tags > a")]
    )


def get_page_quotes(url: str, quotes: list[Quote]) -> None:
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")

    quotes.extend(
        [
            parse_single_quote(quote_soup)
            for quote_soup in soup.select(".quote")
        ]
    )

    next_page = soup.select_one(".next > a")
    if next_page is not None:
        get_page_quotes(urljoin(URL, next_page["href"]), quotes)


def get_all_quotes() -> list[Quote]:
    quotes = []
    get_page_quotes(URL, quotes)

    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    with open(output_csv_path, "w") as file:
        csv_file = csv.writer(file)
        csv_file.writerow([field.name for field in fields(Quote)])
        csv_file.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
