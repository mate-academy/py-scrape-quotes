import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    born_date: str
    born_location: str
    description: str


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


def get_soup(session: requests.Session, url: str) -> BeautifulSoup:
    response = session.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags .tag")],
    )


def parse_author(soup: BeautifulSoup) -> Author:
    return Author(
        name=soup.select_one(".author-title").text.strip(),
        born_date=soup.select_one(".author-born-date").text,
        born_location=soup.select_one(".author-born-location").text,
        description=soup.select_one(".author-description").text.strip(),
    )


def collect_authors(
    session: requests.Session,
    soup: BeautifulSoup,
    authors: dict[str, Author],
) -> None:
    for quote in soup.select(".quote"):
        link = quote.select_one("a[href^='/author/']")["href"]
        if link not in authors:
            authors[link] = parse_author(
                get_soup(session, urljoin(BASE_URL, link))
            )


def scrape(
    session: requests.Session,
) -> tuple[list[Quote], dict[str, Author]]:
    quotes = []
    authors = {}
    url = BASE_URL

    while url:
        soup = get_soup(session, url)
        quotes.extend(parse_single_quote(q) for q in soup.select(".quote"))
        collect_authors(session, soup, authors)

        next_link = soup.select_one("li.next > a")
        url = urljoin(BASE_URL, next_link["href"]) if next_link else None

    return quotes, authors


def write_to_csv(
    items: list, fieldnames: list[str], output_csv_path: str
) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(fieldnames)
        writer.writerows(astuple(item) for item in items)


def main(output_csv_path: str) -> None:
    with requests.Session() as session:
        quotes, authors = scrape(session)

    write_to_csv(quotes, QUOTE_FIELDS, output_csv_path)
    write_to_csv(list(authors.values()), AUTHOR_FIELDS, "authors.csv")


if __name__ == "__main__":
    main("quotes.csv")
