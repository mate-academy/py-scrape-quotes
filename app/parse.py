from dataclasses import dataclass
from typing import Generator
from functools import cache
import datetime
import csv
import time

import tqdm
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


hostname = "https://quotes.toscrape.com"
page_base_url = "/page/{page_number}/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.124 Safari/537.36"
)
REQUEST_DELAY = 0.3


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    born_date: datetime.date
    born_location: str
    description: str


def get_pages(
    session: requests.Session,
) -> Generator[BeautifulSoup, None, None]:
    base_url = hostname + page_base_url
    page_number = 1
    while True:
        try:
            response = session.get(base_url.format(page_number=page_number))
            if response.status_code != 200:
                print(
                    f"Failed to fetch page {page_number}: "
                    f"Status code {response.status_code}"
                )
                break
            if "No quotes found!" in response.text:
                break
            yield BeautifulSoup(response.content, "html.parser")
            page_number += 1
            time.sleep(REQUEST_DELAY)
        except RequestException as e:
            print(f"Error fetching page {page_number}: {e}")
            break


@cache
def get_author_about(
    session: requests.Session,
    author_url: str,
) -> Author | None:
    author_url = hostname + author_url
    try:
        response = session.get(author_url)
        if response.status_code != 200:
            print(
                "Failed to fetch author data: "
                f"Status code {response.status_code}"
            )
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        try:
            name = soup.select_one(".author-title").text.strip()
            born_date = datetime.datetime.strptime(
                soup.select_one(".author-born-date").text.strip(), "%B %d, %Y"
            ).date()
            born_location = soup.select_one(
                ".author-born-location"
            ).text.strip()
            description = soup.select_one(".author-description").text.strip()
        except AttributeError as e:
            print(f"Error parsing author data: {e}")
            return None
        time.sleep(REQUEST_DELAY)
    except RequestException as e:
        print(f"Error fetching author data: {e}")
        return None

    return Author(
        name=name,
        born_date=born_date,
        born_location=born_location,
        description=description,
    )


def parse_one_page(
    page: BeautifulSoup,
    session: requests.Session,
    collect_authors: bool = False,
) -> tuple[list[Quote], list[Author | None]]:
    quotes = []
    authors = []
    for quote in page.select(".quote"):
        # quotes
        text = quote.select_one(".text").text.strip()
        author = quote.select_one(".author").text.strip()
        tags = [tag.text.strip() for tag in quote.select(".tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))

        # authors
        if collect_authors:
            author_link = quote.select_one('a[href^="/author/"]')
            if author_link:
                author_url = author_link["href"]
                authors.append(get_author_about(session, author_url))
    return quotes, authors


def main(
    output_csv_path: str,
    authors_csv_path: str = "authors.csv",
    collect_authors: bool = False,
) -> None:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    all_quotes = []
    all_authors: dict[str, Author | None] = {}

    for page in tqdm.tqdm(get_pages(session), "Collect data about all quotes"):
        quotes, authors = parse_one_page(page, session, collect_authors)
        all_quotes.extend(quotes)

        for author in authors:
            if author and author.name not in all_authors:
                all_authors[author.name] = author

    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in tqdm.tqdm(
            all_quotes,
            f"Write all quotes in file: {output_csv_path}",
            total=len(all_quotes)
        ):
            writer.writerow([quote.text, quote.author, str(quote.tags)])

    if collect_authors:
        with open(authors_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "name",
                "born_date",
                "born_location",
                "description"
            ])
            for author in tqdm.tqdm(
                all_authors.values(),
                f"Write all authors in file: {authors_csv_path}",
                total=len(all_authors)
            ):
                writer.writerow([
                    author.name,
                    author.born_date,
                    author.born_location,
                    author.description.replace("\n", " ").strip(),
                ])


if __name__ == "__main__":
    main("quotes.csv")
