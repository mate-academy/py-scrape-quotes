import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

URL = "https://quotes.toscrape.com/"

session = requests.Session()


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = ["author", "bio"]

authors_bio: dict[str, str] = {}


def get_soup(url: str) -> BeautifulSoup:
    response = session.get(url, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def parse_bio(url: str) -> str:
    soup = get_soup(url)
    born_date = soup.select_one(".author-born-date").text
    born_location = soup.select_one(".author-born-location").text
    description = soup.select_one(".author-description").text.strip()
    return f"Born {born_date} {born_location}. {description}"


def cache_author_bio(author: str, author_url: str) -> None:
    if author not in authors_bio:
        authors_bio[author] = parse_bio(author_url)


def parse_single_quote(quote: Tag) -> Quote:
    author = quote.select_one(".author").text
    author_url = urljoin(URL, quote.select_one("a[href^='/author']")["href"])
    cache_author_bio(author, author_url)

    return Quote(
        text=quote.select_one(".text").text,
        author=author,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def parse_one_page(soup: BeautifulSoup) -> list[Quote]:
    return [parse_single_quote(quote) for quote in soup.select("div.quote")]


def parse_all_pages(url: str) -> list[Quote]:
    quotes = []

    while url:
        soup = get_soup(url)
        quotes.extend(parse_one_page(soup))

        next_link = soup.select_one("li.next > a")
        url = urljoin(url, next_link["href"]) if next_link else None

    return quotes


def write_csv(path: str, header: list[str], rows: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def main(output_csv_path: str) -> None:
    quotes = parse_all_pages(URL)

    write_csv(output_csv_path, QUOTE_FIELDS, [astuple(q) for q in quotes])
    write_csv("authors.csv", AUTHOR_FIELDS, list(authors_bio.items()))


if __name__ == "__main__":
    main("quotes.csv")
