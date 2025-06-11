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
    birth_date: str
    location: str
    description: str


QUOTES_FIELDS = [field.name for field in fields(Quote)]
AUTHORS_FIELDS = [field.name for field in fields(Author)]


def parse_single_quote(quote: Tag) -> tuple[Quote, str]:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags = [tag.text for tag in quote.select(".tag")]
    author_link = quote.select_one("span > a")["href"]

    return Quote(text=text, author=author, tags=tags), author_link


def parse_single_author(author_relative_url: str) -> Author:
    url = urljoin(BASE_URL, author_relative_url)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")

    name = soup.select_one("h3.author-title").text.strip()
    birth_date = soup.select_one("span.author-born-date").text.strip()
    birth_location = soup.select_one("span.author-born-location").text.strip()
    description = soup.select_one("div.author-description").text.strip()

    return Author(
        name=name,
        birth_date=birth_date,
        location=birth_location,
        description=description
    )


def parse_all_pages() -> tuple[list[Quote], dict[str, Author]]:
    all_quotes = []
    authors = {}

    page_counter = 1
    while True:
        page_url = urljoin(BASE_URL, f"page/{page_counter}/")
        response = requests.get(page_url)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, "lxml")
        quotes = soup.select(".quote")
        for quote in quotes:
            quote, author_link = parse_single_quote(quote)
            all_quotes.append(quote)

            if quote.author not in authors:
                author = parse_single_author(author_link)
                authors[quote.author] = author

        next_btn = soup.select_one("li.next > a")
        if not next_btn:
            break

        page_counter += 1

    return all_quotes, authors


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_authors_to_csv(
        output_csv_path: str,
        authors: dict[str, Author]
) -> None:
    with open(output_csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(AUTHORS_FIELDS)
        writer.writerows([astuple(author) for author in authors.values()])


def main(output_csv_path: str) -> None:
    quotes, authors = parse_all_pages()
    write_quotes_to_csv(output_csv_path, quotes)

    write_authors_to_csv("author.csv", authors)


if __name__ == "__main__":
    main("quotes.csv")
