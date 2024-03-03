import csv
from dataclasses import dataclass, fields, astuple
from typing import List

import requests
from bs4 import BeautifulSoup, Tag

URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    @classmethod
    def parse_one_quote(cls, quote_soup: Tag) -> "Quote":
        all_tags = quote_soup.select(".tag")
        list_of_tags = [tag.text for tag in all_tags]

        return Quote(
            text=quote_soup.select_one(".text").text,
            author=quote_soup.select_one(".author").text,
            tags=list_of_tags
        )


CLASS_FIELDS = [field.name for field in fields(Quote)]


def parse_quotes_on_one_page(page_soup: BeautifulSoup) -> List[Quote]:
    quotes = page_soup.select(".quote")

    return [Quote.parse_one_quote(quote) for quote in quotes]


def parse_all_quotes() -> List[Quote]:
    page = requests.get(URL).content
    soup = BeautifulSoup(page, "html.parser")

    current_page_number = 2

    all_quotes = parse_quotes_on_one_page(soup)

    while True:
        page = requests.get(f"{URL}/page/{current_page_number}/").content
        soup = BeautifulSoup(page, "html.parser")

        all_quotes.extend(parse_quotes_on_one_page(soup))

        next_page = weather_next_page(soup)

        if next_page is None:
            break

        current_page_number += 1

    return all_quotes


def weather_next_page(page_soup: Tag) -> int | None:
    next_page = page_soup.select(".pager .next")

    if not next_page:
        return None

    return 1


def main(output_csv_file: str) -> None:
    quotes = parse_all_quotes()

    with open(output_csv_file, "w") as file:
        writer = csv.writer(file)
        writer.writerow(CLASS_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
