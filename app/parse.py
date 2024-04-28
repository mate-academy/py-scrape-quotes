import csv
from dataclasses import dataclass, fields

import requests
from bs4 import BeautifulSoup


QUOTES_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_tags(tags: BeautifulSoup) -> list[str]:
    return [
        tag.text
        for tag in tags
    ]


def get_single_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=get_tags(quote.select(".tag"))
    )


def get_single_page_quotes(soup: BeautifulSoup) -> [Quote]:
    quotes = soup.select(".quote")

    return [get_single_quote(quote) for quote in quotes]


def get_quotes() -> [Quote]:
    page = requests.get(QUOTES_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(soup)
    next_page_link = soup.select_one(".next")

    while next_page_link:
        next_page = requests.get(QUOTES_URL + next_page_link.a["href"]).content
        soup = BeautifulSoup(next_page, "html.parser")
        all_quotes += get_single_page_quotes(soup)

        next_page_link = soup.select_one(".next")

    return all_quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        for quote in quotes:
            writer.writerow(getattr(quote, field) for field in QUOTE_FIELDS)


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
