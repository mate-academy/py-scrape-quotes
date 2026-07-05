import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(element: Tag) -> Quote:
    return Quote(
        text=element.select_one("span.text").text,
        author=element.select_one("small.author").text,
        tags=[tag.text for tag in element.select("a.tag")],
    )


def get_single_page_quotes(soup: BeautifulSoup) -> list[Quote]:
    elements = soup.select("div.quote")
    return [parse_single_quote(element) for element in elements]


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    current_url = BASE_URL

    while current_url:
        response = requests.get(current_url)
        soup = BeautifulSoup(response.text, "html.parser")

        all_quotes.extend(get_single_page_quotes(soup))

        next_button = soup.select_one("li.next a")
        current_url = (
            urljoin(BASE_URL, next_button["href"]) if next_button else None
        )

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
