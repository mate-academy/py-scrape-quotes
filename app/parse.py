import csv
from dataclasses import dataclass, fields
from typing import List

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_next_page_url(index: int) -> str:
    return BASE_URL + f"page/{index}/"


def parse_quotes(page_url: str) -> List[Quote]:
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")

    quotes = [
        parse_single_quote(q_elem)
        for q_elem in soup.select(".quote")
    ]

    next_page = soup.select_one(".next > a")
    if next_page is not None:
        quotes.extend(
            parse_quotes(
                BASE_URL + next_page["href"]
            )
        )

    return quotes


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = quote_soup.select_one(".tags").text.split("\n")[3:-1]
    return Quote(
        text=text,
        author=author,
        tags=tags,
    )


def main(output_csv_path: str) -> None:
    quotes = parse_quotes(BASE_URL)
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [field.name for field in fields(Quote)]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([quote.__dict__ for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
