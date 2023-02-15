import csv
import time
import requests

from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    biography: str


QUOTE_FIELDS = [field.name for field in fields(Quote)]
QUOTE_FIELDS_AUTHOR = [field.name for field in fields(Author)]


def parse_single_quote(page_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=page_soup.select_one(".text").text,
        author=page_soup.select_one(".author").text,
        tags=[tag.text for tag in page_soup.select(".tag")]
    )


def parse_author(page_soup: BeautifulSoup) -> Author:
    return Author(
        biography=page_soup.select_one(
            ".author-title"
        ).text.replace("\n", " "),
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_single_page_authors(page_soup: BeautifulSoup) -> [str]:
    quotes = page_soup.select(".quote")
    return [quote.select_one("a").get("href") for quote in quotes]


def get_page_soup(page_soup: BeautifulSoup = None) -> BeautifulSoup:
    if page_soup:
        pagination = page_soup.select_one(".next > a").get("href")
        next_url = urljoin(BASE_URL, pagination)
        page = requests.get(next_url).content
        page_soup = BeautifulSoup(page, "html.parser")
        return page_soup
    page = requests.get(BASE_URL).content
    page_soup = BeautifulSoup(page, "html.parser")
    return page_soup


def get_author_bio(set_author_urls: {str}) -> [Author]:
    list_author_bio = []
    for author_url in set_author_urls:
        url_author = urljoin(BASE_URL, author_url)
        page = requests.get(url_author).content
        page_soup = BeautifulSoup(page, "html.parser")

        list_author_bio.append(parse_author(page_soup))
    return list_author_bio


def get_quotes() -> ([Quote], [Author]):
    list_quote = []
    list_authors_url = []
    page_soup = get_page_soup()

    next_page = True
    while next_page:
        list_quote.extend(
            get_single_page_quotes(page_soup)
        )
        list_authors_url.extend(
            get_single_page_authors(page_soup)
        )

        if not page_soup.find("li", class_="next"):
            next_page = False
        else:
            page_soup = get_page_soup(page_soup)

    list_author_bio = get_author_bio(set(list_authors_url))
    return list_quote, list_author_bio


def write_quotes_in_file(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_authors_in_file(authors: [Author], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS_AUTHOR)
        writer.writerows([astuple(author) for author in authors])


def main(output_csv_path: str = None) -> None:
    quotes, authors = get_quotes()
    write_quotes_in_file(quotes, output_csv_path)
    write_authors_in_file(authors, "authors.csv")


if __name__ == "__main__":
    star = time.perf_counter()
    main("quotes.csv")
    print(f"Elapsed: {time.perf_counter() - star}")
