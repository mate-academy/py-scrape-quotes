import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "http://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return (Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    ))


def get_quotes() -> list[Quote]:
    quotes = []
    url = BASE_URL
    while True:
        content = requests.get(url).content
        soup = BeautifulSoup(content, "html.parser")
        quotes.extend([parse_single_quote(q) for q in soup.select(".quote")])
        next_btn = soup.select_one("li.next > a")
        if next_btn:
            next_url = next_btn["href"]
            url = BASE_URL.rstrip("/") + next_url
        else:
            break
    return quotes


def write_quotes_to_csv(quotes: list[Quote], path: str = "quotes.csv") -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quotes) for quotes in quotes])


def main(path: str = "quotes.csv") -> None:
    write_quotes_to_csv(get_quotes(), path)


if __name__ == "__main__":
    main("quotes.csv")
