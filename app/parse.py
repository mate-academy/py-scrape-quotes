import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com/"


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


def get_quotes() -> list[Quote]:
    all_quotes: list[Quote] = []
    current_page_url = BASE_URL

    while current_page_url:
        response = requests.get(current_page_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        quotes = soup.select(".quote")
        all_quotes.extend(parse_single_quote(quote) for quote in quotes)

        next_page = soup.select_one(".next a")
        if next_page:
            current_page_url = urljoin(BASE_URL, next_page["href"])
        else:
            current_page_url = None

    return all_quotes


def write_quotes_to_csv(
    quotes: list[Quote],
    output_csv_path: str,
) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
