import csv
import time

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, fields, astuple

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name.capitalize() for field in fields(Quote)]


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_quotes_from_page(soup: BeautifulSoup) -> list[Quote]:
    quote_elements = soup.select(".quote")
    quotes = []
    for element in quote_elements:
        text = element.select_one(".text").get_text(strip=True)
        author = element.select_one(".author").get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag in element.select(".tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))
    return quotes


def get_author_bio(author_url: str, cache: dict) -> str:
    if author_url in cache:
        return cache[author_url]

    full_url = BASE_URL + author_url
    soup = get_soup(full_url)
    bio = soup.select_one(".author-description").get_text(strip=True)
    cache[author_url] = bio
    time.sleep(0.5)
    return bio


def main(output_csv_path: str) -> None:
    all_quotes: list[Quote] = []
    author_bios = {}
    author_cache = {}

    next_page = "/"
    while next_page:
        soup = get_soup(BASE_URL + next_page)
        quote_elements = soup.select(".quote")
        parse_quotes = parse_quotes_from_page(soup)
        all_quotes.extend(parse_quotes)

        # Get author bio (only once per author)
        for element in quote_elements:
            author = element.select_one(".author").get_text(strip=True)
            author_url = element.select_one("a")["href"]
            if author not in author_cache:
                bio = get_author_bio(author_url, author_cache)
                author_bios[author] = bio

        next_btn = soup.select_one(".next > a")
        next_page = next_btn["href"] if next_btn else None
        time.sleep(0.5)

    # Write quotes to CSV
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in all_quotes])

    # Save author bios
    with open("authors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Author", "Biography"])
        writer.writerows([[author, bio]
                          for author, bio in author_bios.items()])


if __name__ == "__main__":
    main("quotes.csv")
