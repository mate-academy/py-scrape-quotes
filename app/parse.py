import csv
from dataclasses import dataclass, astuple

import requests
from bs4 import BeautifulSoup, Tag


FIELDS = ["text", "author", "tags"]


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select("a.tag")]
    )


def get_quotes() -> list[Quote]:
    page_num = 1
    objects = []
    while True:
        page = requests.get(
            f"https://quotes.toscrape.com/page/{page_num}/"
        ).content
        soup = BeautifulSoup(page, "html.parser")

        quotes = soup.select(".quote")
        res = [parse_single_quote(quote) for quote in quotes]

        objects.extend(res)
        page_num += 1
        if not res:
            break
    return objects


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    with open(output_csv_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)
        writer.writerows([astuple(quote_obj) for quote_obj in quotes])


if __name__ == "__main__":
    main("quotes.csv")
