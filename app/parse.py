from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def get_quotes():
    content = requests.get(BASE_URL).content
    soup = BeautifulSoup(content, "html.parser")

    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def main(output_csv_path: str) -> None:
    print(get_quotes())

if __name__ == "__main__":
    main("quotes.csv")
