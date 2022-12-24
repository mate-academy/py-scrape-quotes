import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"
OUTPUT_CSV_PATH = "quotes.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_singe_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = [tag.text for tag in quote_soup.select(".tag")]

    return Quote(
        text=text,
        author=author,
        tags=tags,
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_singe_quote(quote) for quote in quotes]


def get_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(soup)
    next_li_tag = soup.select_one(".next")

    while next_li_tag:
        next_page = next_li_tag.select_one("a")["href"]
        page = requests.get(BASE_URL + next_page)
        soup = BeautifulSoup(page.text, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        next_li_tag = soup.select_one(".next")

    return all_quotes


def main(output_csv_path: str) -> None:
    with open(
            output_csv_path, "w", newline="", encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows(
            [
                astuple(quote)
                for quote in get_quotes()
            ]
        )


if __name__ == "__main__":
    main("quotes.csv")
