import csv
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
START_PAGE = "/page/1/"


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
    bio: str


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = [tag.text for tag in quote_soup.select(".tag")]

    return Quote(text=text, author=author, tags=tags)


def parse_author(author_soup: BeautifulSoup) -> Author:
    name = author_soup.select_one(".author-title").text.strip()
    birth_date = author_soup.select_one(".author-born-date").text.strip()
    birth_place = author_soup.select_one(".author-born-location").text.strip()
    bio = author_soup.select_one(".author-description")
    bio = bio.text.strip().replace("\n", " ")

    return Author(
        name=name,
        birth_date=birth_date,
        birth_place=birth_place,
        bio=bio
    )


def parse_quotes_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes_soup = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes_soup]


def scrape_pagination(page_soup: BeautifulSoup) -> str | None:
    next_page = page_soup.select_one(".next > a")
    return next_page["href"] if next_page else None


def scrape_author(author_url: str) -> Author:
    response = requests.get(urljoin(BASE_URL, author_url))
    author_soup = BeautifulSoup(response.text, "html.parser")
    return parse_author(author_soup)


def scrape_quotes(
    base_url: str, start_page: str
) -> (list[Quote], list[Author]):
    all_quotes = []
    all_authors = {}
    next_page = start_page

    while next_page:
        response = requests.get(urljoin(base_url, next_page))
        page_soup = BeautifulSoup(response.text, "html.parser")

        quotes = parse_quotes_page(page_soup)
        all_quotes.extend(quotes)

        for quote_soup in page_soup.select(".quote"):
            author_url = quote_soup.select_one(".author + a")["href"]
            if author_url not in all_authors:
                all_authors[author_url] = scrape_author(author_url)

        next_page = scrape_pagination(page_soup)

    return all_quotes, list(all_authors.values())


def save_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def save_authors_to_csv(authors: list[Author], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["name", "birth_date", "birth_place", "bio"])
        for author in authors:
            writer.writerow(
                [author.name, author.birth_date, author.birth_place,
                 author.bio]
            )


def main(*output_csv_paths: str) -> None:
    if len(output_csv_paths) < 1:
        raise ValueError("At least one output CSV path is required.")

    quote_csv_path = output_csv_paths[0]

    quotes, authors = scrape_quotes(BASE_URL, START_PAGE)
    save_quotes_to_csv(quotes, quote_csv_path)

    if len(output_csv_paths) > 1:
        author_csv_path = output_csv_paths[1]
        save_authors_to_csv(authors, author_csv_path)


if __name__ == "__main__":
    main("quotes.csv", "authors.csv")
