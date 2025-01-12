import csv

from dataclasses import dataclass, fields, astuple

import httpx
from bs4 import BeautifulSoup, Tag


URL = "https://quotes.toscrape.com/"
NUM_PAGES = 10


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags_html = quote.select(".tag")
    return Quote(
        text=text,
        author=author,
        tags=[tag.text for tag in tags_html]
    )


def get_quotes() -> [Quote]:
    all_quotes = []
    with httpx.Client() as client:
        for i in range(1, NUM_PAGES + 1):
            content = client.get(f"{URL}page/{i}/").content
            soup = BeautifulSoup(content, "html.parser")
            quotes = soup.select(".quote")
            all_quotes += [parse_single_quote(quote) for quote in quotes]
    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    with open(output_csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
