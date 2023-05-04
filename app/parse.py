from dataclasses import dataclass

import requests
import csv
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    biography: str
    birthday: str
    location_born: str


URL = "https://quotes.toscrape.com"
CSV_QUOTE_FIELDS = ["text", "author", "tags"]
CSV_AUTHOR_FIELDS = ["name", "biography", "birthday", "location_born"]


def write_links_to_author_page(links: set[str]) -> None:
    with open("links_to_author_page.txt", "w") as file:
        for link in links:
            file.write(f"{link}\n")


def write_authors_to_csv(
        authors: list[Author],
        path: str = "authors.csv"
) -> None:
    with open(path, "w", newline="", encoding="UTF-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_AUTHOR_FIELDS)
        writer.writeheader()

        for author in authors:
            writer.writerow({**author.__dict__})


def write_quotes_to_csv(path: str, quotes: list[Quote]) -> None:
    with open(path, "w", newline="", encoding="UTF-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_QUOTE_FIELDS)
        writer.writeheader()

        for quote in quotes:
            writer.writerow({**quote.__dict__})


def get_next_page(soup: BeautifulSoup) -> str | None:
    try:
        return URL + soup.select_one(".pager .next a")["href"]
    except TypeError:
        return None


def get_single_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags = [tag.text for tag in quote.select(".tag")]

    return Quote(text, author, tags)


def get_quotes() -> list[Quote]:
    all_quotes = []
    all_authors = set()

    next_page = URL + "/page/1/"

    while next_page:
        response = requests.get(next_page)
        soup = BeautifulSoup(response.content, "html.parser")
        next_page = get_next_page(soup)

        quotes = soup.select(".quote")

        all_quotes.extend(quotes)
        all_authors.update(
            a["href"] for a in soup.select(".quote span a")
        )

    write_links_to_author_page(all_authors)

    return [get_single_quote(quote) for quote in all_quotes]


def get_authors() -> list[Author]:
    with open("links_to_author_page.txt", "r") as file:
        links = [link.strip() for link in file.readlines()]
    all_authors = []

    for link in links:
        response = requests.get(URL + link)
        soup = BeautifulSoup(response.content, "html.parser")

        name = soup.select_one("h3.author-title").text.strip().split("\n")[0]
        biography = soup.select_one(".author-description").text.strip()
        birthday = soup.select_one(".author-born-date").text.strip()
        location_born = (
            soup.select_one(".author-born-location")
            .text.strip().replace("in ", "")
        )
        author = Author(
            name=name,
            biography=biography,
            birthday=birthday,
            location_born=location_born
        )
        all_authors.append(author)

    return all_authors


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    authors = get_authors()

    write_quotes_to_csv(output_csv_path, quotes)
    write_authors_to_csv(authors)


if __name__ == "__main__":
    main("quotes.csv")
