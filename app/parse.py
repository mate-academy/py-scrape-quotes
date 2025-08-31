import csv
from dataclasses import dataclass, fields

import requests
from bs4 import BeautifulSoup, Tag
from requests import RequestException

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

# authors cache (dict: link -> Author)
author_cache: dict[str, Author] = {}


def parse_single_author(author_link: str) -> Author:
    if author_link in author_cache:
        return author_cache[author_link]

    try:
        response = requests.get(BASE_URL + author_link)
        response.raise_for_status()
        author_page = BeautifulSoup(response.content, "html.parser")
    except RequestException as e:
        print(f"Warning: Could not fetch author page {author_link}: {e}")
        return Author(name="", born_date="", born_location="", description="")

    author = Author(
        name=author_page.select_one(".author-title").text.strip(),
        born_date=author_page.select_one(".author-born-date").text.strip(),
        born_location=author_page.select_one(
            ".author-born-location"
        ).text.strip(),
        description=author_page.select_one(".author-description").text.strip()
    )

    author_cache[author_link] = author
    return author


def parse_single_quote(quote: Tag) -> Quote:
    author_link = quote.select_one("small.author + a")["href"]
    parse_single_author(author_link)

    return Quote(
        text=str(quote.select_one(".text").text),
        author=str(quote.select_one(".author").text),
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_page_quotes() -> list[Quote]:
    try:
        first_page_response = requests.get(BASE_URL)
        first_page_response.raise_for_status()
        first_page = BeautifulSoup(first_page_response.content, "html.parser")
    except RequestException as e:
        print(
            f"Warning: Could not fetch quotes first page page {BASE_URL}: {e}"
        )
        return [Quote(text="", author="", tags=[""])]

    all_quotes = get_single_page_quotes(first_page)
    next_page_link = first_page.select_one("li.next a")["href"]

    while next_page_link:
        try:
            next_page_response = requests.get(BASE_URL + next_page_link)
            next_page_response.raise_for_status()
            next_page = BeautifulSoup(
                next_page_response.content, "html.parser"
            )
        except RequestException as e:
            print(
                f"Warning: Could not fetch quotes next page page "
                f"{BASE_URL + next_page_link}: {e}"
            )
            break

        all_quotes.extend(get_single_page_quotes(next_page))
        next_page = next_page.select_one("li.next a")
        if next_page:
            next_page_link = next_page["href"]
        else:
            next_page_link = None

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([
            (quote.text, quote.author, str(quote.tags))
            for quote in quotes
        ])


def write_authors_to_csv(
        authors: dict[str, Author],
        output_csv_path: str
) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows([
            (
                author.name,
                author.born_date,
                author.born_location,
                author.description
            )
            for author in authors.values()
        ])


def main(output_csv_path: str) -> None:
    quotes = get_page_quotes()
    write_quotes_to_csv(quotes, output_csv_path)
    write_authors_to_csv(author_cache, "authors.csv")


if __name__ == "__main__":
    main("quotes.csv")
