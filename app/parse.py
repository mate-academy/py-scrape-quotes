from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin
import time

import requests
from bs4 import BeautifulSoup, Tag
import csv


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


FIELDS = [field.name for field in fields(Quote)]


def get_page_number(page: Tag) -> int | None:
    next_page = page.select_one(".next a")
    if next_page is None:
        return None
    return int(next_page["href"].rstrip("/").split("/")[-1])


def get_single_page_quotes(page: Tag) -> list[Quote]:
    quotes = page.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def parse_quotes() -> list[Quote]:
    text = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(text, "html.parser")
    all_quotes = get_single_page_quotes(first_page_soup)
    next_page = get_page_number(first_page_soup)
    while next_page is not None:
        page_url = urljoin(BASE_URL, f"page/{next_page}/")
        time.sleep(1)
        text = requests.get(page_url).content
        next_page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(next_page_soup))
        next_page = get_page_number(next_page_soup)
    return all_quotes


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def write_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_to_csv(parse_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
