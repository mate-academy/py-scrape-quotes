import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

QUOTES_URL = "https://quotes.toscrape.com"


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


QUOTES_FIELDS = [field.name for field in fields(Quote)]
AUTHORS_FIELDS = [field.name for field in fields(Author)]


def get_or_fetch_author(
    author_relative_url: str,
    session: requests.Session,
    authors_cache: dict[str, Author],
) -> Author:
    if author_relative_url in authors_cache:
        return authors_cache[author_relative_url]

    full_url = urljoin(QUOTES_URL, author_relative_url)
    response = session.get(full_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    name_el = soup.select_one(".author-title")
    born_date_el = soup.select_one(".author-born-date")
    born_loc_el = soup.select_one(".author-born-location")
    desc_el = soup.select_one(".author-description")

    author = Author(
        name=name_el.get_text(strip=True) if name_el else "",
        born_date=born_date_el.get_text(strip=True) if born_date_el else "",
        born_location=born_loc_el.get_text(strip=True) if born_loc_el else "",
        description=desc_el.get_text(strip=True) if desc_el else "",
    )

    authors_cache[author_relative_url] = author
    return author


def parse_single_quote(
    quote: Tag,
    session: requests.Session,
    authors_cache: dict[str, Author],
) -> Quote:
    author_link_tag = quote.select_one("span a[href^='/author/']")
    if author_link_tag:
        get_or_fetch_author(author_link_tag["href"], session, authors_cache)

    return Quote(
        text=quote.select_one(".text").get_text(strip=True),
        author=quote.select_one(".author").get_text(strip=True),
        tags=[tag.get_text(strip=True) for tag in quote.select(".tag")],
    )


def get_single_page_quotes(
    page_soup: Tag,
    session: requests.Session,
    authors_cache: dict[str, Author],
) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [
        parse_single_quote(quote, session, authors_cache) for quote in quotes
    ]


def scrape_all_data() -> tuple[list[Quote], list[Author]]:
    base_url = f"{QUOTES_URL}/page/{{}}/"
    page = 1
    all_quotes: list[Quote] = []
    authors_cache: dict[str, Author] = {}

    with requests.Session() as session:
        while True:
            response = session.get(base_url.format(page))
            if 'class="quote"' not in response.text:
                break

            soup = BeautifulSoup(response.text, "html.parser")
            all_quotes.extend(
                get_single_page_quotes(soup, session, authors_cache)
            )
            page += 1

    return all_quotes, list(authors_cache.values())


def write_to_csv(file_path: str, fieldnames: list[str], rows: list) -> None:
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        writer.writerows([astuple(row) for row in rows])


def main(
    output_csv_path: str,
    authors_csv_path: str = "authors.csv",
) -> None:
    quotes, authors = scrape_all_data()
    write_to_csv(output_csv_path, QUOTES_FIELDS, quotes)
    write_to_csv(authors_csv_path, AUTHORS_FIELDS, authors)


if __name__ == "__main__":
    main("quotes.csv", "authors.csv")
