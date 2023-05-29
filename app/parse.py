import csv
from dataclasses import astuple, dataclass, fields

import requests as requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELD = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_quotes() -> [Quote]:
    base_url = BASE_URL
    quotes = []

    while base_url:
        page = requests.get(base_url).content
        soup = BeautifulSoup(page, "html.parser")

        quotes += soup.select(".quote")

        next_class = soup.find("li", class_="next")

        if next_class:
            next_page = next_class.find("a")
            next_url = next_page["href"]
            base_url = BASE_URL + next_url
        else:
            base_url = None

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELD)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
