import csv
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


HOME_URL = "https://quotes.toscrape.com/"
author_urls = {}
author_instances = []


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    born: str
    description: str


def parse_single_author(quote_soup: Tag) -> str:
    author_href = quote_soup.select_one("a")["href"]

    if author_href not in author_urls:
        author_url = urljoin(HOME_URL, author_href)
        author_page = requests.get(author_url).content
        author_soup = BeautifulSoup(author_page, "html.parser")

        name = quote_soup.select_one("small.author").text
        born = author_soup.select_one(".author-details p").text[6:]
        description = author_soup.select_one(
            ".author-description"
        ).text.strip()

        author_urls[author_href] = name
        author_instances.append(
            Author(name=name, born=born, description=description)
        )
    else:
        name = author_urls[author_href]

    return name


def parse_single_quote(quote_soup: Tag) -> Quote:
    name = parse_single_author(quote_soup)

    return Quote(
        text=quote_soup.select_one("span.text").text,
        author=name,
        tags=[tag.text for tag in quote_soup.select("a.tag")],
    )


def get_all_quotes() -> list[Quote]:
    quotes_list = []
    page_url = HOME_URL

    while True:
        page = requests.get(page_url).content
        soup = BeautifulSoup(page, "html.parser")

        quotes = soup.select("div.quote")
        quotes_list.extend(
            parse_single_quote(quotes_soup) for quotes_soup in quotes
        )

        next_page_link = soup.select_one("li.next a")
        if not next_page_link:
            break

        page_url = urljoin(HOME_URL, next_page_link["href"])

    return quotes_list


def save_authors(output_csv_path: str) -> None:
    with open(
        output_csv_path, mode="w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["name", "born", "description"])

        for author in author_instances:
            writer.writerow([author.name, author.born, author.description])


def main(output_csv_path: str) -> None:
    with open(
        output_csv_path, mode="w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])

        for quote in get_all_quotes():
            writer.writerow([quote.text, quote.author, quote.tags])

    save_authors("authors.csv")


if __name__ == "__main__":
    main("quotes.csv")
