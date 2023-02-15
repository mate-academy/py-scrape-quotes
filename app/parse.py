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


def write_quotes_in_file(quotes: [Quote], output_csv_path: str) -> None:
    quote_fields = [field.name for field in fields(Quote)]
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(quote_fields)
        writer.writerows([astuple(quote) for quote in quotes])


def write_authors_in_file(authors: [Author]) -> None:
    author_fields = [field.name for field in fields(Author)]
    with open("authors.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(author_fields)
        writer.writerows([astuple(author) for author in authors])


def get_authors_page_soup(
        page_soup: list[BeautifulSoup]
) -> list[BeautifulSoup]:
    list_authors = []
    for author_url in page_soup:
        url = urljoin(
            BASE_URL,
            author_url.select_one("a").get("href")
        )
        if url not in AUTHORS_URL_SET:
            page = requests.get(url).content
            list_authors.append(BeautifulSoup(page, "html.parser"))
        AUTHORS_URL_SET.add(url)
    return list_authors


def get_all_page_soup() -> list[BeautifulSoup]:
    list_page_soup = []

    page = requests.get(BASE_URL).content
    page_soup = BeautifulSoup(page, "html.parser")
    list_page_soup.append(page_soup.select(".quote"))

    while page_soup.find("li", class_="next"):
        pagination = page_soup.select_one(".next > a").get("href")
        next_url = urljoin(BASE_URL, pagination)
        page = requests.get(next_url).content
        page_soup = BeautifulSoup(page, "html.parser")
        list_page_soup.append(page_soup.select(".quote"))
    return list_page_soup


def get_quotes(list_page_soup: BeautifulSoup) -> list[Quote]:
    quotes_list = []
    for page_soup in list_page_soup:
        for quote in page_soup:
            quotes_list.append(parse_single_quote(quote))
    return quotes_list


def get_authors(list_page_soup: BeautifulSoup) -> list[Author]:
    authors_list = []
    for page_soup in list_page_soup:
        authors_page_soup = get_authors_page_soup(page_soup)
        for author in authors_page_soup:
            authors_list.append(parse_single_author(author))
    return authors_list


def main(output_csv_path: str) -> None:
    list_page_soup = get_all_page_soup()

    quotes_list = get_quotes(list_page_soup)
    authors_list = get_authors(list_page_soup)
    write_quotes_in_file(quotes_list, output_csv_path)
    write_authors_in_file(authors_list)


if __name__ == "__main__":
    star = time.perf_counter()
    main("quotes.csv")
    print(f"Elapsed: {time.perf_counter() - star}")
