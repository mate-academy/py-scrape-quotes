import csv
import requests

from bs4 import BeautifulSoup, Tag

from dataclasses import dataclass, fields, astuple

BASE_URL = "https://quotes.toscrape.com/"


def get_url(
    base: str = BASE_URL, page_num: int = 1
) -> str:
    return base + f"page/{page_num}/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:

    quote = Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select_one(".tags").select(".tag")]
    )
    return quote


def get_quotes(page_number: int = 1) -> [Quote]:

    data = requests.get(get_url(BASE_URL, page_number)).text
    soup = BeautifulSoup(data, "html.parser")
    quotes = soup.select(".quote")
    all_quotes = [parse_single_quote(quote) for quote in quotes]

    while soup.select_one(".next"):
        page_number += 1
        data = requests.get(get_url(BASE_URL, page_number)).text
        soup = BeautifulSoup(data, "html.parser")
        quotes = soup.select(".quote")
        all_quotes.extend([parse_single_quote(quote) for quote in quotes])

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes(1)
    with open(output_csv_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([field.name for field in fields(Quote)])
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
