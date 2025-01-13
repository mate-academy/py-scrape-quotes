import csv
from dataclasses import dataclass, astuple
from typing import Generator
import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin

URL = "https://quotes.toscrape.com/"

CACHE_OF_AUTHORS = {}


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Bio:
    author: str
    born: str
    description: str


def extract_bio(author: str) -> None:
    if author in CACHE_OF_AUTHORS:
        return
    new_author = (
        author.replace(". ", "-")
        .replace(" ", "-")
        .replace(".", "-")
        .replace("'", "")
        .replace("é", "e")
        .rstrip("-")
    )
    url = urljoin(URL, f"author/{new_author}/")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    born = soup.select_one("span.author-born-date").text
    description = soup.select_one("div.author-description").text.strip()

    bio = Bio(author=author, born=born, description=description)

    CACHE_OF_AUTHORS[author] = bio


def extract_quote(product: Tag) -> Quote:
    text = product.select_one("span.text").text
    author = product.select_one("small.author").text
    tags = [tag.text for tag in product.select("a.tag")]
    extract_bio(author)
    return Quote(
        text=text,
        author=author,
        tags=tags,
    )


def parse_quotes(page_content: bytes) -> list[Quote]:
    soup = BeautifulSoup(page_content, "html.parser")
    product_tags = soup.select(".quote")
    return [extract_quote(tag) for tag in product_tags]


def page_generator(url: str) -> Generator[bytes, None, None]:
    page_num = 1
    while True:
        page_url = urljoin(url, f"page/{page_num}/")
        response = requests.get(page_url)
        if len(response.text) < 3050:
            break
        yield response.content
        page_num += 1


def scrape_quotes() -> list[Quote]:
    quotes = []
    for page in page_generator(URL):
        quotes.extend(parse_quotes(page))
    return quotes


def write_to_file(quotes: list[Quote], file_name: str) -> None:
    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])

    with open("authors_bio.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["author", "birthdate", "description"])
        writer.writerows(
            [astuple(author) for author in CACHE_OF_AUTHORS.values()]
        )


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    write_to_file(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
