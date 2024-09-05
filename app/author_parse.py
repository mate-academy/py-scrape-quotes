import csv
from dataclasses import dataclass, fields, asdict
import os
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup, Tag


AUTHORS_CSV = "authors.csv"
BASE_URL = "http://quotes.toscrape.com/"


@dataclass
class Author:
    name: str
    born: str
    biography: str


AUTHOR_FIELDS = [field.name for field in fields(Author)]


authors = []
if os.path.exists(AUTHORS_CSV):
    with open(AUTHORS_CSV, "r") as authors_csv:
        reader = csv.reader(authors_csv)
        for row in reader:
            authors.append(row[0])


def save_authors_to_csv(author: Author) -> None:
    try:
        is_empty = os.stat(AUTHORS_CSV).st_size == 0
    except FileNotFoundError:
        is_empty = True
    with open(AUTHORS_CSV, "a") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=AUTHOR_FIELDS)
        if is_empty:
            writer.writeheader()
        writer.writerow(asdict(author))


async def parse_single_author(author_soup: Tag) -> None:
    global authors
    author_name = author_soup.select_one(".author").text

    if author_name not in authors:
        authors.append(author_name)
        author_url = urljoin(BASE_URL, author_soup.select_one("a")["href"])
        async with httpx.AsyncClient() as client:
            author_details = await client.get(
                author_url, follow_redirects=True
            )
            author_details_soup = BeautifulSoup(
                author_details.content, "html.parser"
            )
            author = Author(
                name=author_name,
                born=author_details_soup.select_one(".author-born-date").text
                + author_details_soup.select_one(".author-born-location").text,
                biography=author_details_soup.select_one(
                    ".author-description"
                ).text.strip(),
            )
            save_authors_to_csv(author)
