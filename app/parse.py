import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_page_content(page_number):
    page = requests.get(f"{BASE_URL}/page/{page_number}").content
    page_content = BeautifulSoup(page, "html.parser")
    return page_content


def parse_single_page_quote(quote_soup: BeautifulSoup):
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags_soup = quote_soup.select(".tags")
    tags = [tag.text.replace("Tags:", "").split() for tag in tags_soup][0]
    return Quote(
        text=text,
        author=author,
        tags=tags
    )


def get_quotes_info() -> [Quote]:
    page_number = 1
    all_quotes = get_page_content(page_number=page_number).select(".quote")
    pagination = get_page_content(page_number).select(".next")
    while pagination:
        page_number += 1
        print(f"parsing {page_number} page")
        all_quotes.extend(get_page_content(page_number).select(".quote"))
        pagination = get_page_content(page_number).select(".next")

    return [parse_single_page_quote(quote_soup) for quote_soup in all_quotes]


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in get_quotes_info())


if __name__ == "__main__":
    main("quotes.csv")
