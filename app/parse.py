import csv
import requests

from urllib.parse import urljoin
from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"

VISITED_AUTHORS_URLS = []


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


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


def parse_single_quote(soup: BeautifulSoup) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=[
            tag_soup.text
            for tag_soup in soup.select(".tags > .tag")
        ]
    )


def parse_single_author(soup: BeautifulSoup) -> Author:
    return Author(
        full_name=soup.select_one(".author-title").text,
        born=(soup.select_one(".author-born-date").text
              + soup.select_one(".author-born-location").text),
        description=soup.select_one(".author-description").text
    )


def parse_author_biography_page(soup: BeautifulSoup) -> Author | None:
    identifier = soup.select_one("span > a")["href"]
    url = urljoin(BASE_URL, identifier)

    if url in VISITED_AUTHORS_URLS:
        return None

    VISITED_AUTHORS_URLS.append(url)
    page = requests.get(url).content
    authors_page_soup = BeautifulSoup(page, "html.parser")

    return parse_single_author(authors_page_soup.select_one(".author-details"))


def get_single_page_quotes(soup: BeautifulSoup) -> [Quote]:
    quotes_soup = soup.select(".quote")

    quotes = []
    for quote in quotes_soup:
        quotes.append(parse_single_quote(quote))
        author = parse_author_biography_page(quote)

        if author:
            write_to_csv([author], AUTHOR_FIELDS, "authors.csv", "a")

    return quotes


def get_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    quotes = get_single_page_quotes(soup)

    page_num = 2
    while soup.select_one(".next"):
        new_url = urljoin(BASE_URL, f"/page/{page_num}")
        page = requests.get(new_url).content
        soup = BeautifulSoup(page, "html.parser")

        quotes.extend(get_single_page_quotes(soup))

        page_num += 1

    return quotes


def write_to_csv(
        objects: [dataclass],
        fields: list[str],
        output_csv_path: str,
        flag: str
) -> None:
    with open(output_csv_path, flag, newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        writer.writerows([astuple(object) for object in objects])


def main(output_csv_path: str) -> None:
    write_to_csv(
        get_quotes(),
        QUOTE_FIELDS,
        output_csv_path,
        "w"
    )


if __name__ == "__main__":
    main("quotes.csv")
