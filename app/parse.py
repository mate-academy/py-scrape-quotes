import requests
from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup, Tag
import csv
import time

HOME_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_single_page_quote(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> list[Quote]:
    all_quotes = []
    next_page_url = HOME_URL

    while next_page_url:
        time.sleep(1)
        response = requests.get(next_page_url)
        soup = BeautifulSoup(response.content, "lxml")

        all_quotes.extend(get_single_page_quote(soup))

        next_button = soup.select_one(".next > a")
        if next_button:
            next_page_url = HOME_URL + next_button["href"]
        else:
            next_page_url = None

    return all_quotes


def write_quotes_to_scv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_scv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
