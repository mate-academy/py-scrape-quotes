import csv
from dataclasses import dataclass, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


FIELD_NAMES = [field.name for field in fields(Quote)]


def parse_single_quote(soup: BeautifulSoup) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=find_tags(soup)
    )


def find_tags(soup: BeautifulSoup) -> list[str]:
    tags = soup.select(".tags .tag")
    return [tag.text for tag in tags]


def get_page_link(soup: BeautifulSoup) -> str:
    page_soup = soup.select_one(".pager > li.next > a")
    if page_soup is None:
        return "end"
    return page_soup.get("href")


def get_single_page_quotes(soup: BeautifulSoup) -> [Quote]:
    quotes = soup.select(".quote")
    return [parse_single_quote(quotes_soup) for quotes_soup in quotes]


def main(output_csv_path: str) -> None:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    all_quotes = get_single_page_quotes(soup)

    while True:
        page = requests.get(urljoin(BASE_URL, get_page_link(soup))).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))

        if get_page_link(soup) == "end":
            break

    with open(output_csv_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(FIELD_NAMES)
        for quote in all_quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
