import csv
import time
from dataclasses import dataclass, astuple, fields
from typing import Generator

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "http://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags = quote.find_all("a", class_="tag")
    tag_list = [t.get_text().strip() for t in tags]

    return Quote(
        text=text,
        author=author,
        tags=tag_list,
    )


def parse_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = []
    for quote in page_soup.select(".quote"):
        quotes.append(parse_single_quote(quote))
    return quotes


def page_generator() -> Generator[BeautifulSoup, None, None]:
    page_number = 1
    with requests.Session() as session:
        while page_number != 11:
            request_url = f"{BASE_URL}page/{page_number}/"
            response = session.get(url=request_url)
            soup = BeautifulSoup(response.content, "html.parser")
            yield soup
            page_number += 1
            time.sleep(0.2)


def get_quotes() -> list[Quote]:
    quotes = []
    num = 1
    for page_soup in page_generator():
        print(f"Parsing page {num}")
        num += 1
        parsed_quotes = parse_page(page_soup)
        quotes.extend(parsed_quotes)
    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(q) for q in quotes])
    print(f"Saved {len(quotes)} quotes to {output_csv_path}")


if __name__ == "__main__":
    main("quotes.csv")
