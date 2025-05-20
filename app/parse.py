from dataclasses import dataclass, fields, astuple
import csv

import requests
from bs4 import BeautifulSoup, Tag


URL = "https://quotes.toscrape.com/"

@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]

def get_next_page(soup: BeautifulSoup) -> str | None:
    pagination = soup.select_one("li.next > a")
    if pagination:
        return pagination.attrs["href"]


def parse_quote(page: Tag) -> Quote:
    quote = Quote(
        text=page.select_one(".text").text,
        author=page.select_one(".author").text,
        tags=[tag.text for tag in page.select(".tag")]
    )
    return quote


def scrape_quotes_single_page(soup: Tag) -> list[Quote]:
    quotes = soup.select(".quote")
    return [parse_quote(quote) for quote in quotes]


def scrape_quotes() -> list[Quote]:
    response = requests.get(URL).content
    first_page = BeautifulSoup(response, "html.parser")
    all_quotes = scrape_quotes_single_page(first_page)
    next_page = get_next_page(first_page)
    while next_page:
        response = requests.get(URL + next_page).content
        soup = BeautifulSoup(response, "html.parser")
        all_quotes.extend(scrape_quotes_single_page(soup))
        next_page = get_next_page(soup)
    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], name: str) -> None:
    with open(name, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)
        for quote in quotes:
            writer.writerow(astuple(quote))
    

def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
