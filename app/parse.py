from dataclasses import dataclass, astuple
import csv

from bs4 import BeautifulSoup, Tag
import requests


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


URL = "https://quotes.toscrape.com/"


def parse_single_quote(quate_soup: Tag) -> Quote:
    return Quote(
        text=quate_soup.select_one("span.text").text,
        author=quate_soup.select_one("small.author").text,
        tags=quate_soup.select_one("div.tags").text.split()[1:],
    )


def parse_quotes(soup: BeautifulSoup) -> [Quote]:
    quotes = soup.select("div.quote")
    return [parse_single_quote(quote) for quote in quotes]


def to_csv(csv_file: str, quotes: list[Quote]) -> None:
    with open(csv_file, "a") as fh:
        writer = csv.writer(fh, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    current_url = URL
    while True:
        page = requests.get(current_url).content
        soup = BeautifulSoup(page, "html.parser")
        to_csv(output_csv_path, parse_quotes(soup))

        next_page = soup.select_one(".next a")
        if not next_page:
            break
        current_url = URL + next_page["href"]


if __name__ == "__main__":
    main("quotes.csv")
