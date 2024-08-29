import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

FILE_NAME = "output_csv_path"
BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_one_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = quote_soup.select_one(".keywords")

    if tags and tags.has_attr("content"):
        tags_content = tags["content"]
        if tags_content:
            tags = tags_content.split(",")
        else:
            tags = []
    else:
        tags = []

    return Quote(text=text, author=author, tags=tags)


def get_all_quotes() -> [Quote]:
    page = 1
    res = []
    while True:
        web = requests.get(f"{BASE_URL}/page/{page}").content
        soup = BeautifulSoup(web, "html.parser")
        quotes = soup.select(".quote")
        next_button = soup.select_one(".next")

        res.extend([parse_one_quote(quote_soup) for quote_soup in quotes])

        if not next_button:
            break

        page += 1

    return res


def write_quotes_to_csv(quotes: [Quote], filename: str) -> None:
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
