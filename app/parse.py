import csv

import requests
from dataclasses import dataclass, astuple

from bs4 import BeautifulSoup, Tag

BASE_USR = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:
    tags_raw = quote.select_one(".keywords")["content"]
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=tags_raw.split(",") if tags_raw else [],
    )


def get_first_page_quotes(result: list) -> None:
    text = requests.get(BASE_USR).content
    soup = BeautifulSoup(text, "html.parser")
    quote_list = soup.select(".quote")
    quotes = [parse_single_quote(quote) for quote in quote_list]
    result.extend(quotes)


def get_next_page_quotes(result: list) -> None:
    num_page = 2
    while True:
        url = f"{BASE_USR}/page/{num_page}/"
        response = requests.get(url)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, "html.parser")
        quote_list = soup.select(".quote")

        if not quote_list:
            break

        result.extend([parse_single_quote(quote) for quote in quote_list])

        if not soup.select_one(".next"):
            break
        num_page += 1


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    result = []
    get_first_page_quotes(result=result)
    get_next_page_quotes(result=result)
    print(f"Found {len(result)} quotes")
    write_quotes_to_csv(output_csv_path, quotes=result)


if __name__ == "__main__":
    main("quotes.csv")
