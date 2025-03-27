import csv
from dataclasses import dataclass, fields, astuple
import requests

from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[
            tag.text
            for tag in quote.find_all(
                name="a",
                attrs={"class": "tag"}
            )
        ]
    )


def parse_quotes() -> [Quote]:
    current_page = 1
    result = []

    while True:
        content = requests.get(f"{BASE_URL}page/{current_page}/").content
        soup = BeautifulSoup(content, "html.parser")
        quotes = soup.select(".quote")

        if not quotes:
            break

        result.extend([parse_single_quote(quote) for quote in quotes])
        current_page += 1

    return result


def main(output_csv_path: str) -> None:
    with open(
            output_csv_path,
            "w",
            encoding="utf-8",
            newline=""
    ) as source_file:
        writer = csv.writer(source_file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in parse_quotes()])


if __name__ == "__main__":
    main("quotes.csv")
