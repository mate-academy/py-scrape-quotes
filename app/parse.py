import csv
import time

import requests

from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


author_bio_cache = {}


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()

    return BeautifulSoup(response.content, "html.parser")


def parse_quotes(soup: BeautifulSoup) -> list[Quote]:
    quotes = soup.find_all("div", class_="quote")
    result = []

    for quote in quotes:
        text = quote.find("span", class_="text").get_text(strip=True)
        author = quote.find("small", class_="author").get_text(strip=True)
        tags = [
            tag.get_text(strip=True)
            for tag in quote.find_all("a", class_="tag")
        ]

        result.append(Quote(text=text, author=author, tags=tags))

    return result


def get_next_page(soup: BeautifulSoup, current_url: str) -> str | None:
    next_page = soup.find("li", class_="next")

    if not next_page:
        return None

    next_url = next_page.find("a")["href"]
    return urljoin(current_url, next_url)


def get_all_quotes() -> list[Quote]:
    url = "https://quotes.toscrape.com/"
    all_quotes = []

    while url:
        soup = get_soup(url)
        all_quotes.extend(parse_quotes(soup))
        url = get_next_page(soup, url)
        time.sleep(1)

    return all_quotes


def save_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([
                quote.text,
                quote.author,
                str(quote.tags),
            ])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    save_to_csv(quotes, output_csv_path)

    author_bios = get_all_author_bios()
    authors_csv_path = output_csv_path.replace(".csv", "_authors.csv")
    save_author_bios_to_csv(author_bios, authors_csv_path)


def parse_author_urls(soup: BeautifulSoup, current_url: str) -> dict:
    author_urls = {}

    quotes = soup.find_all("div", class_="quote")

    for quote in quotes:
        author = quote.find("small", class_="author").get_text(strip=True)
        author_link = quote.find("a", href=True)

        author_url = urljoin(current_url, author_link["href"])
        author_urls[author] = author_url

    return author_urls


def get_all_author_urls() -> dict:
    url = "https://quotes.toscrape.com/"
    all_author_urls = {}

    while url:
        soup = get_soup(url)
        all_author_urls.update(parse_author_urls(soup, url))
        url = get_next_page(soup, url)
        time.sleep(1)

    return all_author_urls


def get_author_bio(url: str) -> str:
    if url in author_bio_cache:
        return author_bio_cache[url]

    soup = get_soup(url)
    bio = soup.find("div", class_="author-description")

    result = bio.get_text(strip=True) if bio else ""

    author_bio_cache[url] = result

    return result


def get_all_author_bios() -> dict[str, str]:
    author_urls = get_all_author_urls()
    author_bios = {}

    for author, url in author_urls.items():
        author_bios[author] = get_author_bio(url)

    return author_bios


def save_author_bios_to_csv(
    author_bios: dict[str, str],
    output_csv_path: str,
) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(["author", "bio"])

        for author, bio in author_bios.items():
            writer.writerow([author, bio])


if __name__ == "__main__":
    main("quotes.csv")
