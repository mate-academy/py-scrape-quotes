import csv
from dataclasses import dataclass, astuple, fields

import requests
from bs4 import BeautifulSoup, Tag

QUOTES_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def create_quote_instance(quote: Tag) -> Quote:
    print(type(quote))
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def parse_quotes(page: int = 1) -> list[Quote]:

    result = []

    text = requests.get(f"{QUOTES_URL}/page/{page}/").content
    soup = BeautifulSoup(text, "html.parser")

    quotes = soup.select(".quote")
    result.extend([create_quote_instance(quote) for quote in quotes])

    next_page = soup.select_one(".next")

    if next_page:
        result.extend(parse_quotes(page + 1))

    return result


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([field.name for field in fields(Quote)])
        writer.writerows([astuple(q) for q in quotes])


def main(output_csv_path: str) -> None:
    quotes_data = parse_quotes()
    write_quotes_to_csv(output_csv_path, quotes_data)


if __name__ == "__main__":
    main("quotes.csv")
