import csv
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def write_quotes_to_csv(csv_path: str, quotes: [Quote]) -> None:
    with open(csv_path, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags > .tag")]
    )


def is_there_next_page(soup: BeautifulSoup) -> bool:
    pagination = soup.select_one(".pager > .next > a")

    if pagination is None:
        return False

    return True


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(soup)

    page_num = 2

    while is_there_next_page(soup):
        page = requests.get(
            urljoin(BASE_URL, f"page/{str(page_num)}/")
        ).content
        soup = BeautifulSoup(page, "html.parser")

        all_quotes.extend(get_single_page_quotes(soup))

        page_num += 1

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    write_quotes_to_csv(
        csv_path=output_csv_path, quotes=quotes
    )


if __name__ == "__main__":
    main("quotes.csv")
