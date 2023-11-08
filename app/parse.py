import csv

import requests
from bs4 import BeautifulSoup

from dataclasses import dataclass, fields, astuple


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").get_text(),
        author=quote_soup.select_one(".author").get_text(),
        tags=[
            tag.get_text() for tag in quote_soup.select(".tag")
        ]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:
    all_quotes = []
    base_url = "https://quotes.toscrape.com/"
    current_url = base_url

    while True:
        page = requests.get(current_url).content
        soup = BeautifulSoup(page, "html.parser")

        all_quotes.extend(get_single_page_quotes(soup))

        next_page = soup.find("li", class_="next")
        if not next_page:
            break

        next_url = next_page.find("a")["href"]
        current_url = base_url.rstrip("/") + next_url

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
