import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"
HOME_URL = BASE_URL


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    biography: str


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


def parse_single_quote(quote: Tag) -> Quote:
    """Parse a single quote"""
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def author_bio(author_ulr: str) -> str:
    """Load and return an author's biography"""
    response = requests.get(author_ulr)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    bio = soup.select_one(".author-description").text.strip()
    return bio


def get_all_quotes_and_authors() -> (list[Quote], list[Author]):
    """Parse all quotes and authors with their bio"""
    quotes = []
    authors_cache = {}
    next_page_url = HOME_URL

    while next_page_url:
        # Download page
        response = requests.get(next_page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Collect quotes from current page
        for quote in soup.select(".quote"):
            parsed_quote = parse_single_quote(quote)
            quotes.append(parsed_quote)

            # Check if the author is already cached
            if parsed_quote.author not in authors_cache:
                author_link = quote.select_one(".author + a")["href"]
                author_url = urljoin(BASE_URL, author_link)
                authors_cache[parsed_quote.author] = Author(
                    name=parsed_quote.author,
                    biography=author_bio(author_url),
                )
        # Find link for the next page
        next_page = soup.select_one(".next > a")
        next_page_url = (
            urljoin(BASE_URL, next_page["href"]) if next_page else None
        )
    return quotes, list(authors_cache.values())


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)  # write header
        writer.writerows([astuple(quote) for quote in quotes])  # write rows


def write_authors_to_csv(authors: [Author], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(AUTHOR_FIELDS)  # write header
        writer.writerows(
            [astuple(author) for author in authors]
        )  # write rows


def main(output_csv_path: str, authors_csv_path: str) -> None:

    quotes, authors = get_all_quotes_and_authors()

    # Write quotes and authors to CSV
    write_quotes_to_csv(quotes, output_csv_path)
    write_authors_to_csv(authors, authors_csv_path)

    print(f"Quotes have been saved to {output_csv_path}")
    print(f"Authors have been saved to {authors_csv_path}")


if __name__ == "__main__":
    main("quotes.csv", "authors.csv")
