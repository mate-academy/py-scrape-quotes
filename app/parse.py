from dataclasses import dataclass

import csv
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com"
URL_FOR_PARSE = BASE_URL + "/page/"

AUTHORS = {}


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    born: str
    authors_bio: str


def create_author(authors_name: str, url: str) -> None:
    if authors_name not in AUTHORS:
        page = requests.get(BASE_URL + url).content
        soup = BeautifulSoup(page, "html.parser")

        born = (
            soup.select_one(".author-born-date").text
            + " - "
            + soup.select_one(".author-born-location").text
        )
        authors_bio = soup.select_one(".author-description").text.strip()

        AUTHORS[authors_name] = Author(
            name=authors_name, born=born, authors_bio=authors_bio
        )
        print(authors_name)


def get_quote(quote: BeautifulSoup) -> Quote:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags = [tags.text for tags in quote.select(".tag")]

    author_link = quote.select_one(".author").parent.select_one("a")["href"]

    create_author(author, author_link)

    return Quote(text=text, author=author, tags=tags)


def parse_page(soup: BeautifulSoup) -> list[Quote]:
    quotes_on_page = soup.select(".row > .col-md-8 > .quote")
    quotes = []

    for quote in quotes_on_page:
        quotes.append(get_quote(quote))

    return quotes


def get_all_quotes() -> list[Quote]:
    quotes = []
    number_of_page = 1

    while True:
        page = requests.get(URL_FOR_PARSE + str(number_of_page)).content
        soup = BeautifulSoup(page, "html.parser")

        if "No quotes found!" in soup.select("div.col-md-8")[-1].text:
            break

        quotes.extend(parse_page(soup))

        number_of_page += 1

    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for quote in quotes:
            writer.writerow(
                {
                    "text": quote.text,
                    "author": quote.author,
                    "tags": quote.tags,
                }
            )

    with open("authors.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["name", "born", "authors_bio"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for author in AUTHORS.values():
            writer.writerow(
                {
                    "name": author.name,
                    "born": author.born,
                    "authors_bio": author.authors_bio,
                }
            )


if __name__ == "__main__":
    main("quotes.csv")
