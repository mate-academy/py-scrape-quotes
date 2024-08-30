import csv
from dataclasses import dataclass, astuple
from typing import Generator
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one("span.text").text,
        author=quote_soup.select_one("small.author").text,
        tags=[tag.text for tag in quote_soup.select("a.tag")],
    )


def fetch_page_content(page_url: str) -> bytes | None:
    try:
        response = requests.get(page_url)
        response.raise_for_status()

        return response.content

    except requests.HTTPError as e:
        return print(e)


def page_generator() -> Generator[BeautifulSoup, None, None]:
    page_counter = 2

    while True:
        page_url = urljoin(BASE_URL, f"page/{page_counter}")
        page_content = fetch_page_content(page_url)

        soup = BeautifulSoup(page_content, "html.parser")

        if not soup.select_one(".next"):
            yield soup
            break

        yield soup
        page_counter += 1


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> list[Quote]:
    first_page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(first_page, "html.parser")

    print("Scraping page 1...")
    all_quotes = get_single_page_quotes(first_page_soup)

    for page_num, page in enumerate(page_generator(), start=2):
        print(f"Scraping page {page_num}...")
        all_quotes.extend(get_single_page_quotes(page))

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    print(quotes)
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
