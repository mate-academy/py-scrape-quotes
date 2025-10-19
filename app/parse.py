from dataclasses import dataclass
from typing import Generator
from functools import cache
import datetime
import csv

import tqdm
import requests
from bs4 import BeautifulSoup


hostname = "https://quotes.toscrape.com"
page_base_url = "/page/{page_number}/"


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


def get_pages() -> Generator[BeautifulSoup, None, None]:
    base_url = hostname + page_base_url
    page_number = 1
    while True:
        response = requests.get(base_url.format(page_number=page_number))
        if response.status_code != 200 or "No quotes found!" in response.text:
            break
        yield BeautifulSoup(response.content, "html.parser")
        page_number += 1


@cache
def get_author_about(author_url: str) -> Author | None:
    author_url = hostname + author_url
    response = requests.get(author_url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    try:
        name = soup.select_one(".author-title").text.strip()
        born_date = datetime.datetime.strptime(
            soup.select_one(".author-born-date").text.strip(), "%B %d, %Y"
        ).date()
        born_location = soup.select_one(".author-born-location").text.strip()
        description = soup.select_one(".author-description").text.strip()
    except AttributeError:
        return None

    return Author(
        name=name,
        born_date=born_date,
        born_location=born_location,
        description=description,
    )


def parse_one_page(
    page: BeautifulSoup,
    collect_authors: bool = False
) -> tuple[list[Quote], list[Author]]:
    quotes = []
    authors = []
    for quote in page.select(".quote"):
        # quotes
        text = quote.select_one(".text").text
        author = quote.select_one(".author").text
        tags = [tag.text for tag in quote.select(".tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))

        # authors
        if collect_authors:
            author_url = quote.select_one("a")["href"]
            authors.append(get_author_about(author_url))
    return quotes, authors


def main(
    output_csv_path: str,
    authors_csv_path: str = "authors.csv",
    collect_authors: bool = False
) -> None:
    all_quotes = []
    all_authors: dict[str, Author] = {}

    for page in tqdm.tqdm(get_pages(), "Collect data about all quotes"):
        quotes, authors = parse_one_page(page, collect_authors)
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
