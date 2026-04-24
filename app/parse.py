import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return (Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    ))


def get_single_page_quote() -> [Quote]:
    text = requests.get(BASE_URL).content
    soup = BeautifulSoup(text, "html.parser")
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def write_quotes_to_csv(quotes: [Quote], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        write = csv.writer(f)
        write.writerow(QUOTES_FIELDS)
        write.writerows([astuple(quote) for quote in quotes])


def get_all_quotes() -> [Quote]:
    url = BASE_URL
    all_quotes = []
    while True:
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        quotes = soup.select(".quote")
        all_quotes.extend([parse_single_quote(quote) for quote in quotes])
        next_button = soup.select_one("li.next a")

        if not next_button:
            break

        url = urljoin(BASE_URL, next_button["href"])
    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
