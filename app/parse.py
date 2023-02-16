import csv
import time
import requests

from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://quotes.toscrape.com"
AUTHORS_URL_SET = set()


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    biography: str


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


def parse_single_quote(page_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=page_soup.select_one(".text").text,
        author=page_soup.select_one(".author").text,
        tags=[tag.text for tag in page_soup.select(".tag")]
    )


def parse_single_author(page_soup: BeautifulSoup) -> Author:
    return Author(
        biography=page_soup.select_one(
            ".author-details"
        ).text.replace("\n", " "),
    )


def write_list_in_file(
        name_path_file_csv: str,
        name_file: list[object],
        fields: list[fields],
) -> None:
    with open(name_path_file_csv, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        writer.writerows([astuple(name) for name in name_file])


def get_authors_page_soup(
        page_soup: list[BeautifulSoup]
) -> list[BeautifulSoup]:
    authors = []
    for author_url in page_soup:
        url = urljoin(
            BASE_URL,
            author_url.select_one("a").get("href")
        )
        if url not in AUTHORS_URL_SET:
            page = requests.get(url).content
            authors.append(BeautifulSoup(page, "html.parser"))
        AUTHORS_URL_SET.add(url)
    return authors


def get_all_page_soup() -> list[BeautifulSoup]:
    result_page_soup = []

    page = requests.get(BASE_URL).content
    page_soup = BeautifulSoup(page, "html.parser")
    result_page_soup.append(page_soup.select(".quote"))

    while page_soup.find("li", class_="next"):
        pagination = page_soup.select_one(".next > a").get("href")
        next_url = urljoin(BASE_URL, pagination)
        page = requests.get(next_url).content
        page_soup = BeautifulSoup(page, "html.parser")
        result_page_soup.append(page_soup.select(".quote"))
    return result_page_soup


def get_quotes(list_page_soup: BeautifulSoup) -> list[Quote]:
    result_quotes = []
    for page_soup in list_page_soup:
        for quote in page_soup:
            result_quotes.append(parse_single_quote(quote))
    return result_quotes


def get_authors(list_page_soup: BeautifulSoup) -> list[Author]:
    result_authors = []
    for page_soup in list_page_soup:
        authors_page_soup = get_authors_page_soup(page_soup)
        for author in authors_page_soup:
            result_authors.append(parse_single_author(author))
    return result_authors


def main(output_csv_path: str) -> None:
    page_soup = get_all_page_soup()

    result_quotes = get_quotes(page_soup)
    result_authors = get_authors(page_soup)

    write_list_in_file(
        output_csv_path,
        result_quotes,
        QUOTE_FIELDS
    )
    write_list_in_file(
        "authors.csv",
        result_authors,
        AUTHOR_FIELDS
    )


if __name__ == "__main__":
    star = time.perf_counter()
    main("quotes.csv")
    print(f"Elapsed: {time.perf_counter() - star}")
