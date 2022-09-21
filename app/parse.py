from dataclasses import dataclass, fields

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
    page = requests.get(BASE_URL, params={"page": page_number}).content
    page_content = BeautifulSoup(page, "html.parser")
    return page_content


def parse_single_page_quote(quote_soup: BeautifulSoup):
    pass

def get_quotes_info() -> [Quote]:
    page_number = 1
    all_quotes = get_page_content(page_number=page_number).select(".quote")
    pagination = get_page_content(page_number).select(".next")
    while pagination:
        page_number += 1
        print(f"parsing {page_number} page")
        all_quotes.extend(get_page_content(page_number))
        pagination = 0
        pagination = get_page_content(page_number).select(".next")

    print(all_quotes)






def main(output_csv_path: str) -> None:
    pass


if __name__ == "__main__":
    # main("quotes.csv")
    get_quotes_info()
