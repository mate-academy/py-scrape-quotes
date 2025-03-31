import csv
from dataclasses import dataclass, fields, astuple
from typing import List

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"
QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_page_content(url: str) -> BeautifulSoup:
    response = requests.get(url)
    return BeautifulSoup(response.content, "html.parser")


def extract_quote_data(quote: Tag) -> "Quote":
    return Quote(
        text=quote.select_one("span.text").text,
        author=quote.select_one("small.author").text,
        tags=[tag.text for tag in quote.select("div.tags a")]
    )


def fetch_quotes_from_page(page_num: int, base_url: str) -> List["Quote"]:
    url = f"{base_url}page/{page_num}/"
    page = get_page_content(url)
    quotes = page.select("div.quote")

    return [extract_quote_data(quote) for quote in quotes]


def fetch_quotes(base_url: str) -> List["Quote"]:
    res = []
    page_num = 1

    while True:
        quotes = fetch_quotes_from_page(page_num, base_url)
        if not quotes:
            break
        res.extend(quotes)
        page_num += 1

    return res


def save_quotes_to_csv(quotes: list[Quote], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    save_quotes_to_csv(fetch_quotes(BASE_URL), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
