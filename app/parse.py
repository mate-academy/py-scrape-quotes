import csv
from dataclasses import dataclass, astuple

import requests
from bs4 import BeautifulSoup

from urllib.parse import urljoin


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"
AUTHORS = dict()


def get_url_content(url: str) -> bytes:
    """Get url content & raise exception if error"""
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def add_author(auth_url: str) -> None:
    if AUTHORS.get(auth_url) is None:
        auth_page = get_url_content(urljoin(BASE_URL, auth_url))
        soup = BeautifulSoup(auth_page, "html.parser")
        auth = soup.select_one(".author-details")

        AUTHORS[auth_url] = {
            "title" : auth.select_one(".author-title").text,
            "born" : (auth.select_one(".author-born-date").text
                      + " " + auth.select_one(".author-born-location").text),
            "description" : auth.select_one(".author-description").text,
        }


def next_page_url(page_soup: BeautifulSoup) -> int | None:
    page = page_soup.select_one(".next > a")
    if page is None:
        return None
    page = page.attrs["href"]
    return page


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    quote = Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select("a.tag")],
    )
    author_url = quote_soup.select_one("span > a").attrs["href"]

    add_author(author_url)
    return quote


def get_qoutes(url: str) -> list[Quote]:

    quotes = []
    next_url = ""

    while next_url is not None:
        page = get_url_content(urljoin(url, next_url))
        soup = BeautifulSoup(page, "html.parser")

        next_url = next_page_url(soup)

        qoutes_per_page = soup.select(".row > .col-md-8 .quote")
        quotes.extend([parse_single_quote(qoute) for qoute in qoutes_per_page])

    return quotes


def write_to_csv(quotes: list[Quote], output_file: str) -> None:
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


def write_authors_to_csv(authors: dict, output_file: str) -> None:
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["title", "born", "description"])
        for author in authors.values():
            writer.writerow(
                [author["title"], author["born"], author["description"]]
            )


def main(output_csv_path: str) -> None:
    quotes = get_qoutes(BASE_URL)
    write_to_csv(quotes, output_csv_path)
    write_authors_to_csv(AUTHORS, "authors.csv")


if __name__ == "__main__":
    main("quotes.csv")
