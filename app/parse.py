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


QUOTE_FIELDS = [field.name for field in fields(Quote)]

authors_bio: dict[str, str] = {}


def parse_author_bio(quote: Tag) -> None:
    author = quote.select_one(".author").text
    if author in authors_bio:
        return  # сторінку цього автора вже завантажували

    author_url = urljoin(BASE_URL, quote.select_one(".author + a")["href"])
    author_page = BeautifulSoup(
        requests.get(author_url).content,
        "html.parser")
    authors_bio[author] = author_page.select_one(
        ".author-description").text.strip()


def parse_single_quote(quote: Tag) -> Quote:
    parse_author_bio(quote)
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select("a.tag")],
    )


def get_quotes_from_page(page: BeautifulSoup) -> list[Quote]:
    return [parse_single_quote(quote) for quote in page.select(".quote")]


def parse_all_quotes() -> list[Quote]:
    all_quotes = []
    current_page = BASE_URL

    while current_page:
        response = requests.get(current_page).content
        page = BeautifulSoup(response, "html.parser")

        all_quotes.extend(get_quotes_from_page(page))

        # Шукаємо посилання на наступну сторінку
        next_page = page.select_one("li.next a")
        current_page = urljoin(
            BASE_URL, next_page["href"]) if next_page else None

    return all_quotes


def write_quotes_to_file(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_authors_to_file(output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["author", "bio"])
        writer.writerows(authors_bio.items())


def main(output_csv_path: str, output_authors_path: str = "authors.csv") -> None:
    write_quotes_to_file(parse_all_quotes(), output_csv_path)
    write_authors_to_file(output_authors_path)


if __name__ == "__main__":
    main("quotes.csv", "bios.csv")
