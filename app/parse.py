from dataclasses import dataclass
import time
from urllib.parse import urljoin
import csv

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"
CACHE = {}


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def create_soup_by_page_index(page_index: int) -> BeautifulSoup:
    page_url = urljoin(BASE_URL, f"page/{page_index}")
    page = requests.get(page_url).content
    soup = BeautifulSoup(page, "html.parser")
    return soup


def create_soup_by_url(page_url: str) -> BeautifulSoup:
    page = requests.get(page_url).content
    soup = BeautifulSoup(page, "html.parser")
    return soup


def check_next_page(page_index: int) -> bool:
    soup = create_soup_by_page_index(page_index)
    next_page = soup.find(class_="next")
    if not next_page:
        return False
    return True


def get_author_bio(author_url: str) -> tuple[str, str] | None:
    if author_url in CACHE:
        return

    author_soup = create_soup_by_url(author_url)
    author = author_soup.find(class_="author-title").text
    bio = author_soup.find(class_="author-description").text
    CACHE[author_url] = bio
    return author, bio


def process_csv_file_bio(file_path: str, bios: str) -> None:
    with open(file_path, "a", encoding="UTF8", newline="") as bio_csv_file:
        writer = csv.writer(bio_csv_file)
        for bio in bios:
            if bio is not None:
                writer.writerow(bio)


def process_csv_file_header(file_path: str, header: list[str]) -> None:
    header = header
    with open(
            file_path, "a", encoding="UTF8", newline=""
    ) as output_csv_file:
        writer = csv.writer(output_csv_file)
        writer.writerow(header)


def process_csv_file_quotes(file_path: str, quotes: list[Quote]) -> None:
    with open(file_path, "a", encoding="UTF8", newline="") as output_csv_file:
        writer = csv.writer(output_csv_file)
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def parse_page(page_index: int) -> [Quote]:
    soup = create_soup_by_page_index(page_index)
    quotes = soup.find_all(class_="quote")
    quotes_objects = []
    bios = []

    for quote in quotes:
        text = quote.find(class_="text").text
        author = quote.find(class_="author").text
        tags = [tag.text for tag in quote.find_all(class_="tag")]

        quotes_objects.append(
            Quote(
                text=text,
                author=author,
                tags=tags
            )
        )

        author_url = BASE_URL + quote.find("a")["href"]
        bio = get_author_bio(author_url)
        bios.append(bio)

    return quotes_objects, bios


def main(output_csv_path: str) -> None:
    page_index = 1
    authors_bio_csv_path = "authors_bio.csv"
    process_csv_file_header(authors_bio_csv_path, ["author", "bio"])
    process_csv_file_header(output_csv_path, ["text", "author", "tags"])
    while True:
        quotes, bios = parse_page(page_index=page_index)
        process_csv_file_quotes(output_csv_path, quotes)
        process_csv_file_bio(authors_bio_csv_path, bios)
        if check_next_page(page_index=page_index) is False:
            break
        page_index += 1
        time.sleep(1)


if __name__ == "__main__":
    main("quotes.csv")
