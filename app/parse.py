import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(soup: Tag) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=[tag.text for tag in soup.select(".tags a.tag")]
    )


def get_single_page_quotes(page_soup: Tag) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> list[Quote]:
    all_quotes = []
    page_url = BASE_URL

    while page_url:
        response = requests.get(page_url).content
        page_soup = BeautifulSoup(response, "html.parser")

        all_quotes.extend(get_single_page_quotes(page_soup))

        next_page = page_soup.select_one(".next a")
        if next_page:
            page_url = BASE_URL + next_page["href"]
        else:
            break

    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: [Quote]) -> None:
    with open(
            f"{output_csv_path}",
            "w",
            encoding="utf-8",
            newline=""
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(output_csv_path, get_quotes())


if __name__ == "__main__":
    main("quotes.csv")
