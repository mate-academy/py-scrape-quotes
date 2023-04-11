import csv
from dataclasses import dataclass, fields, astuple
from typing import List

import requests
from bs4 import BeautifulSoup

SCRAPE_HOME_URL = "https://quotes.toscrape.com/"
MAX_PAGE_NUM = 11


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_list_tags(quote_soup: BeautifulSoup) -> List[str]:
    tags_soup = quote_soup.select(".tags > .tag")
    tags = [tag.text for tag in tags_soup]

    return tags


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=parse_list_tags(quote_soup)
    )


def get_url_next_page(page_number: str) -> str:
    url = f"{SCRAPE_HOME_URL}page/{str(page_number)}/"
    return url


def get_single_page_quote(page_soup: BeautifulSoup) -> List[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> List[Quote]:
    current_page_num = 0
    all_quotes = []
    while current_page_num < MAX_PAGE_NUM:
        current_page_num += 1
        url = get_url_next_page(str(current_page_num))
        page = requests.get(url)
        page_soup = BeautifulSoup(page.text, "html.parser")
        all_quotes.extend(get_single_page_quote(page_soup))

    return all_quotes


def write_quotes_to_csv(quotes: List[Quote]) -> None:
    with open("result.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes)


if __name__ == "__main__":
    main("result.csv")
