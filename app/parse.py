from dataclasses import dataclass, astuple
import csv

from bs4 import BeautifulSoup, Tag
import requests


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    born: str
    born_location: str
    description: str


seen_athors = []
URL = "https://quotes.toscrape.com/"


def parse_single_author(quote_soup: Tag) -> Author:
    author_url = quote_soup.select_one(".quote a")["href"]
    author_page = requests.get(URL + author_url).content
    author_soup = BeautifulSoup(author_page, "html.parser")
    author_name = author_soup.select_one(".author-title").text
    seen_athors.append(author_name)
    return Author(
        name=author_name,
        born=author_soup.select_one(".author-born-date").text,
        born_location=author_soup.select_one(".author-born-location").text,
        description=author_soup.select_one(".author-description").text,
    )


def parse_single_quote(quate_soup: Tag) -> Quote:
    return Quote(
        text=quate_soup.select_one("span.text").text,
        author=quate_soup.select_one("small.author").text,
        tags=quate_soup.select_one("div.tags").text.split()[1:],
    )


def parse_quotes(soup: BeautifulSoup) -> [Quote]:
    quotes = soup.select("div.quote")
    return [parse_single_quote(quote) for quote in quotes]


def parse_authors(soup: BeautifulSoup) -> [Author]:
    quotes = soup.select("div.quote")
    return [parse_single_author(quote) for quote in quotes if quote.select_one("small.author").text not in seen_athors]


def to_csv(csv_file: str, instances: list[Quote | Author]) -> None:
    with open(csv_file, "a") as fh:
        writer = csv.writer(fh, delimiter=",")
        writer.writerow(vars(instances[0]))
        writer.writerows([astuple(instance) for instance in instances])


def main(output_csv_path: str) -> None:
    current_url = URL
    quotes = []
    authors = []
    while True:
        page = requests.get(current_url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(parse_quotes(soup))
        authors.extend(parse_authors(soup))
        next_page = soup.select_one(".next a")
        if not next_page:
            break
        current_url = URL + next_page["href"]
    to_csv(output_csv_path, quotes)
    to_csv("authors.csv", authors)


if __name__ == "__main__":
    main("quotes.csv")
