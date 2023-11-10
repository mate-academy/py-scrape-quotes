import json
import requests
import csv
import hashlib
import os

from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Tuple, List


BASE_URL = "https://quotes.toscrape.com/"
AUTHORS_FILE_PATH = "authors.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    birth_date: str
    birth_place: str
    description: str


def get_author_url(quote_info: BeautifulSoup) -> str:
    url_ending = quote_info.select_one("span a[href]").get("href")
    author_url = urljoin(BASE_URL, url_ending)

    return author_url


def get_author_bio(author_url: str) -> Author:
    response = requests.get(author_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        return Author(
            name=soup.select_one(".author-title").text,
            birth_date=soup.select_one(".author-born-date").text,
            birth_place=soup.select_one(".author-born-location").text[3:],
            description=soup.select_one(".author-description").text
        )
    else:
        return None


def fetch_and_cache_author_bio(author_url: str) -> Author:
    cache_key = hashlib.md5(author_url.encode()).hexdigest()

    cache_filename = f"cache/{cache_key}.txt"
    os.makedirs(os.path.dirname(cache_filename), exist_ok=True)

    if os.path.exists(cache_filename):
        with open(cache_filename, "r") as file:
            bio_text = file.read()

            if bio_text:
                author_data = json.loads(bio_text)
                return Author(**author_data)
            else:
                return None
    else:
        author = get_author_bio(author_url)

        if author:
            with open(cache_filename, "w") as file:
                json.dump(asdict(author), file)

        return author


def parse_single_quote(quote_raw: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_raw.select_one(".text").text,
        author=quote_raw.select_one(".author").text,
        tags=[tag.text for tag in quote_raw.select(".tag")]
    )


def scrap_text(base_url: str) -> Tuple[List[Quote], List[Author]]:
    quotes = []
    authors = []
    page_number = 1

    while True:
        page_url = urljoin(base_url, f"page/{page_number}/")
        response = requests.get(page_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            quotes_on_page = soup.select(".quote")

            if not quotes_on_page:
                break

            quotes.extend(
                parse_single_quote(quote) for quote in quotes_on_page
            )

            autors_urls = [get_author_url(quote) for quote in quotes_on_page]

            for url in autors_urls:
                authors.append(fetch_and_cache_author_bio(url))

            page_number += 1
        else:
            break

    return quotes, authors


def write_authors_to_file(authors_list: list) -> None:

    with open(AUTHORS_FILE_PATH, "w", encoding="utf-8", newline="") as file:
        fieldnames = ["name", "birth_date", "birth_place", "description"]
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for author in authors_list:
            if author:
                csv_writer.writerow({
                    "name": author.name,
                    "birth_date": author.birth_date,
                    "birth_place": author.birth_place,
                    "description": author.description
                })


def main(output_csv_path: str) -> None:
    quotes, authors = scrap_text(BASE_URL)

    write_authors_to_file(authors)

    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        fieldnames = ["text", "author", "tags"]
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for quote in quotes:
            csv_writer.writerow({
                "text": quote.text,
                "author": quote.author,
                "tags": quote.tags
            })


if __name__ == "__main__":
    main("quotes.csv")
