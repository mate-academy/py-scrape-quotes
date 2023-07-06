import csv
import re

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List
from urllib.parse import urljoin
from unidecode import unidecode


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


@dataclass
class Author:
    name: str
    bio: str


def scrape_quotes_and_authors(base_url: str) -> (
    tuple[list[Quote], dict[str, Author]]
):
    quotes = []
    authors = {}
    url = base_url
    while url:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        quote_divs = soup.find_all("div", class_="quote")
        for quote_div in quote_divs:
            text = quote_div.find(class_="text").get_text(strip=True)
            author_name = quote_div.find(class_="author").get_text(strip=True)
            author_bio = scrape_author_bio(base_url, author_name)
            if author_name not in authors:
                authors[author_name] = Author(author_name, author_bio)
            tags = [
                tag.get_text(strip=True)
                for tag in quote_div.find_all(class_="tag")
            ]
            quotes.append(Quote(text, author_name, tags))

        next_button = soup.find(class_="next")
        url = urljoin(
            base_url, next_button.find("a")["href"]
        ) if next_button else None

    return quotes, authors


def convert_author_name(author_name: str) -> str:
    return re.sub(
        r"(-)+", "-",
        re.sub(r"[^\w\s-]", "", unidecode(re.sub(r"[\s.]", "-", author_name)))
    ).rstrip("-")


def scrape_author_bio(base_url: str, author_name: str) -> str:
    author_url = urljoin(
        base_url, f"author/{convert_author_name(author_name)}"
    )

    soup = BeautifulSoup(requests.get(author_url).content, "html.parser")
    bio_element = soup.find(class_="author-description")
    bio = bio_element.get_text(strip=True)
    return bio


def write_quotes_and_authors_to_csv(
    quotes: list[Quote],
    authors: dict[str, Author],
    output_quotes_csv_path: str,
    output_authors_csv_path: str
) -> None:
    with (
        open(output_quotes_csv_path, "w", newline="") as result_csv,
        open(output_authors_csv_path, "w", newline="") as authors_csv
    ):
        quotes_writer = csv.writer(result_csv)
        quotes_writer.writerow(["text", "author", "tags"])
        authors_writer = csv.writer(authors_csv)
        authors_writer.writerow(["Author", "Bio"])

        for quote in quotes:
            quotes_writer.writerow(
                [quote.text, quote.author, quote.tags]
            )

        for author in authors.values():
            authors_writer.writerow([author.name, author.bio])


def main(output_quotes_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com"
    output_authors_csv_path = "./authors.csv"
    quotes, authors = scrape_quotes_and_authors(base_url)
    write_quotes_and_authors_to_csv(
        quotes, authors, output_quotes_csv_path, output_authors_csv_path
    )
    print("Scraping completed. Quotes are saved in", output_quotes_csv_path)
    print("Author bios are saved in", output_authors_csv_path)


if __name__ == "__main__":
    main("./result.csv")
