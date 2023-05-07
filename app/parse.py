import csv
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com"
AUTHOR_OUTPUT = "authors.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    born_date: str
    born_location: str
    description: str


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url).content
    return BeautifulSoup(response, "html.parser")


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return (
        Quote(
            text=quote_soup.select_one(".text").text,
            author=quote_soup.select_one(".author").text,
            tags=[tag.text for tag in quote_soup.select(".tag")]
        ),
        quote_soup.select_one("a[href]", string="(about)")["href"]
    )


def parse_single_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    quote_list, author_set = list(), set()
    for quote in quotes:
        quote_obj, author_ref = parse_single_quote(quote)
        quote_list.append(quote_obj)
        author_set.add(author_ref)
    return (quote_list, author_set)


def get_author(author_soup: BeautifulSoup) -> Author:
    return Author(
        name=author_soup.select_one(".author-title").text.split("\n", 1)[0],
        born_date=author_soup.select_one(".author-born-date").text,
        born_location=author_soup.select_one(".author-born-location").text,
        description=(
            author_soup.select_one(".author-description")
            .text.replace("\n", "")
        ),
    )


def get_author_list(author_refs: set[str]) -> list[Author]:
    all_authors = list()
    for author_ref in author_refs:
        author_url = urljoin(BASE_URL, author_ref)
        author_soup = get_soup(author_url)
        all_authors.append(get_author(author_soup))
    return all_authors


def write_to_csv(items: list[dataclass], output_csv_path: str) -> None:
    fields_ = [field.name for field in fields(items[0])]
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields_)
        writer.writerows((astuple(item) for item in items))


def main(output_csv_path: str) -> None:
    soup = get_soup(BASE_URL)
    all_quotes, all_authors = parse_single_page(soup)
    next_page = soup.select(".next > a[href]")
    while next_page:
        next_page_url = urljoin(BASE_URL, next_page[0]["href"])
        soup = get_soup(next_page_url)
        quotes, author_refs = parse_single_page(soup)
        all_quotes.extend(quotes)
        all_authors.update(author_refs)
        next_page = soup.select(".next > a[href]")
    write_to_csv(all_quotes, output_csv_path)
    authors_parsed = get_author_list(all_authors)
    write_to_csv(authors_parsed, AUTHOR_OUTPUT)


if __name__ == "__main__":
    main("quotes.csv")
