import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup, Tag


URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_next_page(page_soup: Tag) -> str:
    pagination = page_soup.select_one("li.next > a")
    if pagination:
        return pagination.attrs["href"]


def parse_single_quote(page_soup: Tag) -> Quote:
    quote = Quote(
        text=page_soup.select_one(".text").text,
        author=page_soup.select_one(".author").text,
        tags=[tag.text for tag in page_soup.select(".tags a")]
    )
    return quote


def scrape_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def scrape_quotes() -> list[Quote]:
    response = requests.get(URL).content
    first_page_soup = BeautifulSoup(response, "html.parser")
    all_quotes = scrape_single_page_quotes(first_page_soup)
    next_page = get_next_page(first_page_soup)
    while next_page:
        response = requests.get(f"{URL}{next_page}").content
        next_page_soup = BeautifulSoup(response, "html.parser")
        all_quotes.extend(scrape_single_page_quotes(next_page_soup))
        next_page = get_next_page(next_page_soup)
    return all_quotes


def write_to_file(quotes: list[Quote], file_name: str) -> None:
    with open(file_name, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    write_to_file(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
