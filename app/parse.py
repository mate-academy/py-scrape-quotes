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


FIELDS = [field.name for field in fields(Quote)]


def get_quote(quote_soup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[
            tag.text for tag in quote_soup.select(".tag")
        ]
    )


def get_single_page_quotes(page_soup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [
        get_quote(quote_soup) for quote_soup in quotes
    ]


def get_all_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    page_soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(page_soup)

    page_num = 2

    while True:
        if page_soup.select(".next"):
            page = requests.get(f"{BASE_URL}page/{page_num}/").content
            page_soup = BeautifulSoup(page, "html.parser")
            all_quotes.extend(get_single_page_quotes(page_soup))
            page_num += 1
        else:
            break

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
