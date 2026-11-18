import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com"

QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> list[Quote]:
    text = requests.get(BASE_URL).content
    page_soup = BeautifulSoup(text, "html.parser")
    all_quotes = get_single_page_quotes(page_soup)

    counter = 1
    while page_soup.select_one(".next"):
        counter += 1
        text = requests.get(f"{BASE_URL}/page/{counter}/").content
        page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(page_soup))

    return all_quotes


def write_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_to_csv(quotes=get_all_quotes(), output_csv_path=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
