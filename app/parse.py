import csv
from dataclasses import dataclass, fields
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


TITLE_FIELDS = [field.name for field in fields(Quote)]


def get_single_quote(quote: Tag) -> Quote:
    return (Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tags .tag")]
    ))


def get_quotes(page_soup: Tag) -> List[Quote]:
    list_of_quotes = page_soup.select(".quote")
    return [get_single_quote(quote) for quote in list_of_quotes]


def get_pagination_page(
        url: str = BASE_URL,
        all_quotes: list = None
) -> List[Quote]:
    if all_quotes is None:
        all_quotes = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    all_quotes.extend(get_quotes(soup))

    next_page_element = soup.select_one("li.next a")

    if next_page_element:
        next_page_url = next_page_element.get("href")
        url = urljoin(BASE_URL, next_page_url)
        return get_pagination_page(url, all_quotes)
    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_pagination_page(BASE_URL)
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(TITLE_FIELDS)
        writer.writerows(
            [
                quote.text,
                quote.author,
                str(quote.tags)
            ] for quote in quotes
        )


if __name__ == "__main__":
    main("quotes.csv")
