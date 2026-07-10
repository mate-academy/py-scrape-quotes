import csv
import dataclasses
from dataclasses import dataclass, astuple

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in dataclasses.fields(Quote)]


URL = "https://quotes.toscrape.com/page/"


def parse_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text")
    author = quote.select_one(".author")

    return Quote(
        text=text.text if text else "No text",
        author=author.text if author else "Unknown",
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_quotes() -> list[Quote]:
    result = []
    page = 1
    while True:
        pagination_url = URL + str(page)
        page += 1
        text = requests.get(pagination_url).content
        soup = BeautifulSoup(text, "html.parser")
        quotes = soup.select(".quote")
        result.extend(parse_quote(quote) for quote in quotes)
        if not quotes:
            break
    return result


def write_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", errors="replace") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    write_to_csv(get_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
