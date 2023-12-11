import csv
from dataclasses import dataclass, astuple, fields

import requests
from bs4 import BeautifulSoup


QUOTES_HOME_PAGE = "https://quotes.toscrape.com/"


def get_page_url(page_num: int) -> str:
    if page_num < 2:
        return QUOTES_HOME_PAGE
    return f"{QUOTES_HOME_PAGE}/page/{page_num}/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select("a.tag")]
    )


def parse_single_page(page_quotes: BeautifulSoup) -> [Quote]:
    return [parse_single_quote(quote) for quote in page_quotes]


def parse_quotes() -> list[Quote]:
    page_num = 1
    quotes = []
    while True:
        print(f"parsing page {page_num}")
        content = requests.get(get_page_url(page_num)).content
        page_soup = BeautifulSoup(content, "html.parser")

        page_quotes = page_soup.select(".quote")
        quotes.extend(parse_single_page(page_quotes))

        next_page = page_soup.select_one("li.next > a[href]")
        if next_page:
            page_num += 1
        else:
            break
    return quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(output_csv_path, parse_quotes())


if __name__ == "__main__":
    main("quotes.csv")
