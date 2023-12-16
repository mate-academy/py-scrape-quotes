from dataclasses import dataclass, astuple
import csv

from bs4 import BeautifulSoup, Tag
import requests


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    def __repr__(self):
        return f"{self.text},{self.author},{self.tags}"


URL = "https://quotes.toscrape.com/"


def parse_single_quote(quate_soup: Tag) -> Quote:
    return Quote(
        text=quate_soup.select_one("span.text").text,
        author=quate_soup.select_one("small.author").text,
        tags=quate_soup.select_one("div.tags").text.split()[1:],
    )


def parse_quotes(url: str) -> [Quote]:
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")

    quotes = soup.select("div.quote")
    return [parse_single_quote(quote) for quote in quotes]


def to_csv(csv_file: str, quotes: list[Quote]) -> None:
    with open(csv_file, "w+") as fh:
        writer = csv.writer(fh, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    page = URL
    to_csv(output_csv_path, parse_quotes(page))


if __name__ == "__main__":
    main("quotes.csv")
