import csv
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
import requests

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


FIELDS_LIST = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags_html = quote.select(".tag")
    return Quote(
        text=text,
        author=author,
        tags=[tag.text for tag in tags_html]
    )


def get_quotes_from_page(base_url: str) -> list[Quote]:
    text = requests.get(base_url).text
    soup = BeautifulSoup(text, "html.parser")
    quotes = soup.select(".quote")

    all_quotes = [parse_single_quote(quote) for quote in quotes]

    next_page = soup.select_one(".next a")

    while next_page:
        url_to_parse = urljoin(BASE_URL, next_page.get("href"))
        text = requests.get(url_to_parse).text
        soup = BeautifulSoup(text, "html.parser")

        quotes = soup.select(".quote")
        all_quotes.extend(parse_single_quote(quote) for quote in quotes)

        next_page = soup.select_one(".next a")

    return all_quotes


def write_quotes_to_csv(path: str, quotes: list[Quote]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(FIELDS_LIST)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    quotes = get_quotes_from_page(BASE_URL)
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
