import csv
import logging
import sys
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ]
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    author: str
    born: str
    description: str


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


def parse_single_author(author_block: BeautifulSoup) -> Author:
    authors = []

    author = author_block.select_one(".author-title").text

    if author in authors:
        return

    authors.append(author)

    born_date = author_block.select_one("span.author-born-date").text
    born_location = author_block.select_one("span.author-born-location").text
    born = f"{born_date} {born_location}"

    description = author_block.select_one(".author-description").text

    return Author(
        author=author,
        born=born,
        description=description
    )


def parse_authors(url: str, quote: BeautifulSoup) -> [Author]:
    author_url = quote.select_one("a")["href"]
    full_author_url = urljoin(url, author_url)

    response = requests.get(full_author_url).content
    soup = BeautifulSoup(response, "html.parser")

    authors = soup.select(".author-details")

    return [parse_single_author(author) for author in authors]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tags .tag")]
    )


def get_quotes_and_authors() -> [Quote]:
    logging.info("Start parsing")

    processed_quotes = []
    processed_authors = []
    page_number = 1

    while True:
        logging.info(f"Start parsing page #{page_number}")

        next_page = urljoin(BASE_URL, f"page/{page_number}/")
        response = requests.get(next_page).content
        soup = BeautifulSoup(response, "html.parser")

        quotes = soup.select(".quote")

        result = [parse_single_quote(quote) for quote in quotes]
        processed_quotes.extend(result)

        for quote in quotes:
            authors = parse_authors(BASE_URL, quote)
            processed_authors.extend(authors)

        # authors = [parse_authors(BASE_URL, quote) for quote in quotes]
        # processed_authors.extend(*authors)

        if not soup.select_one(".pager .next"):
            break

        page_number += 1

    logging.info("Stop parsing")

    return processed_quotes, processed_authors


def write_to_csv(
        output_csv_path: str,
        quotes: [Quote] = None,
        authors: [Author] = None
) -> None:
    logging.info("Start writing quotes to file")
    data = quotes if quotes else authors
    headers = QUOTE_FIELDS if quotes else AUTHOR_FIELDS

    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows([astuple(row) for row in data])

        logging.info("Writing to file completed successfully")


def main(output_csv_path: str) -> None:
    quotes, authors = get_quotes_and_authors()
    write_to_csv(output_csv_path, quotes)

    authors_file = "authors.csv"

    write_to_csv(authors_file, authors)


if __name__ == "__main__":
    main("quotes.csv")
