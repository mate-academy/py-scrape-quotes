import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

URL = "http://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = [tag.text for tag in quote_soup.select(".tag")]

    return Quote(text, author, tags)


def parse_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_soup(url: str) -> BeautifulSoup:
    with requests.Session() as session:
        response = session.get(url)
    return BeautifulSoup(response.content, "html.parser")


def get_all_quotes() -> list[Quote]:
    first_page_soup = get_soup(URL)
    all_quotes = parse_single_page_quotes(first_page_soup)
    next_page = first_page_soup.select_one(".next > a")

    while next_page:
        page_soup = get_soup(f'{URL}{next_page.attrs["href"]}')
        all_quotes.extend(parse_single_page_quotes(page_soup))
        next_page = page_soup.select_one(".next > a")

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(Quote.__dataclass_fields__.keys())
        writer.writerows(
            [(quote.text, quote.author, quote.tags) for quote in quotes]
        )


if __name__ == "__main__":
    main("quotes.csv")
