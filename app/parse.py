from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests
import csv

from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup, ResultSet, Tag

from app.utils import format_name


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    date_of_birth: datetime
    location: str
    biography: str


QUOTE_COLUMNS = [field.name for field in fields(Quote)]
AUTHOR_COLUMNS = [field.name for field in fields(Author)]

BASE_URL = "https://quotes.toscrape.com"
AUTHOR_URL = f"{BASE_URL}/author"


def parse_single_quote(soup: Tag) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one("span > small[itemprop=author]").text,
        tags=[tag.text for tag in soup.select(".tags > .tag")]
    )


def parse_page_quotes(quotes: ResultSet[Tag]) -> list[Quote]:
    return [parse_single_quote(soup) for soup in quotes]


def parse_author_page(soup: Tag) -> Author:
    name = soup.select_one(".author-title").text
    author_born_date = soup.select_one(".author-born-date").text
    date_of_birth = datetime.strptime(str(author_born_date), "%B %d, %Y")
    location = soup.select_one(".author-born-location").text.replace("in ", "")
    biography = soup.select_one(".author-description").text
    return Author(
        name=name,
        date_of_birth=date_of_birth,
        location=location,
        biography=biography
    )


def fetch_author(author_name: str) -> Author:
    url = f"{AUTHOR_URL}/{format_name(author_name)}"
    with requests.Session() as session:
        response = session.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return parse_author_page(soup)


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_COLUMNS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_authors_to_csv(output_csv_path: str, authors: list[Author]) -> None:
    with open(output_csv_path, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(AUTHOR_COLUMNS)
        writer.writerows([astuple(author) for author in authors])


def get_page_content() -> tuple[list[Quote], list[Author]]:
    page_num = 1
    all_quotes = []
    author_names = {}

    with requests.Session() as session:
        while True:
            request_url = urljoin(BASE_URL, f"/page/{page_num}/")
            response = session.get(request_url)
            soup = BeautifulSoup(response.content, "html.parser")
            page_quotes = soup.find_all("div", class_="quote")

            if not page_quotes:
                break

            quotes_portion = parse_page_quotes(page_quotes)
            all_quotes.extend(quotes_portion)

            for quote in quotes_portion:
                author_names[quote.author] = None

            page_num += 1

    with ThreadPoolExecutor(max_workers=5) as executor:
        fetched_authors = list(
            executor.map(
                fetch_author,
                author_names.keys()
            )
        )

    for name, author in zip(author_names.keys(), fetched_authors):
        author_names[name] = author

    return all_quotes, list(author_names.values())


def main(output_csv_path: str) -> None:
    quotes, authors = get_page_content()
    write_quotes_to_csv(output_csv_path, quotes)
    write_authors_to_csv("authors.csv", authors)


if __name__ == "__main__":
    main("quotes.csv")
