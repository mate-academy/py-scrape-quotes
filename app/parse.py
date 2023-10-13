import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
AUTHOR_LINKS = set()


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    full_name: str
    born: str
    description: str


def get_fields_for_column_names(data_class: dataclass) -> [str]:
    return [field.name for field in fields(data_class)]


def get_single_page_soup(address: int | str) -> BeautifulSoup:
    sub_url = f"page/{address}/" if isinstance(address, int) else address
    quotes_url = urljoin(BASE_URL, sub_url)
    page = requests.get(quotes_url).content
    return BeautifulSoup(page, "html.parser")


def get_authors_page_links(soup: BeautifulSoup) -> None:
    quotes = soup.select(".quote")
    for quote in quotes:
        AUTHOR_LINKS.add(quote.select_one("a").get("href"))


def parse_single_quote(page_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=page_soup.select_one(".text").text,
        author=page_soup.select_one(".author").text,
        tags=[tag.text for tag in page_soup.select(".tag")],
    )


def parse_author(page_soup: BeautifulSoup) -> Author:
    return Author(
        full_name=page_soup.select_one(".author-title").text,
        born=(page_soup.select_one(".author-born-date").text
              + " "
              + page_soup.select_one(".author-born-location").text),
        description=page_soup.select_one(".author-description").text.strip(),
    )


def get_single_page_quotes(soup: BeautifulSoup) -> [Quote]:
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def check_next_page(single_page_soup: BeautifulSoup) -> bool:
    return single_page_soup.find("li", {"class": "next"})


def get_all_quotes(page_number: int = 1) -> [Quote]:
    page_soup = get_single_page_soup(page_number)

    get_authors_page_links(page_soup)
    all_quotes = get_single_page_quotes(page_soup)

    while check_next_page(page_soup):
        page_number += 1
        page_soup = get_single_page_soup(page_number)
        get_authors_page_links(page_soup)
        all_quotes.extend(get_single_page_quotes(page_soup))

    return all_quotes


def get_all_authors() -> [Author]:
    return [parse_author(get_single_page_soup(link)) for link in AUTHOR_LINKS]


def write_quotes_to_csv(
        quotes: [Quote],
        file_path: str,
        class_type: dataclass
) -> None:
    with open(file_path, "w", encoding="UTF-8", newline="") as file:
        writer = csv.writer(file)
        first_row_fields = get_fields_for_column_names(class_type)
        writer.writerow(first_row_fields)
        writer.writerows([astuple(quote) for quote in quotes])


def main(quotes_csv_path: str) -> None:
    quotes = get_all_quotes()
    quotes_class_type = type(quotes[0])
    authors = get_all_authors()
    authors_class_type = type(authors[0])
    write_quotes_to_csv(quotes, quotes_csv_path, quotes_class_type)
    authors_csv_path = "authors.csv"
    write_quotes_to_csv(authors, authors_csv_path, authors_class_type)


if __name__ == "__main__":
    main("quotes.csv")
