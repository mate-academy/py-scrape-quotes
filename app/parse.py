import csv
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"
AUTHOR_URL = urljoin(BASE_URL, "authors/")


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    full_name: str
    born: str
    description: str


QUOTES_FIELDS = [field.name for field in fields(Quote)]
AUTHORS_FIELDS = [field.name for field in fields(Author)]

authors_cache = {}


def parse_single_author(author: Tag) -> Author:
    return Author(
        full_name=author.select_one(".author-title").text.strip(),
        born=author.select_one(".author-born-date").text.strip(),
        description=author.select_one(".author-description").text.strip()
    )


def parse_single_quote(quote: Tag) -> Quote:
    author_url = quote.select_one("a[href^='/author/']")["href"]
    author_page_url = urljoin(BASE_URL, str(author_url))

    if author_url not in authors_cache:
        text = requests.get(author_page_url).content
        author_page_soup = BeautifulSoup(text, "html.parser")
        authors_cache[str(author_url)] = parse_single_author(author_page_soup)

    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select_one(".tags").select(".tag")]
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_page_quotes() -> list[Quote]:
    text = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(text, "html.parser")
    all_quotes = get_single_page_quotes(first_page_soup)

    next_page_link = first_page_soup.select_one("li.next a")

    while next_page_link:
        next_page_url = urljoin(BASE_URL, str(next_page_link["href"]))
        text = requests.get(next_page_url).content
        page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(page_soup))

        next_link = page_soup.select_one("li.next a")
        if next_link:
            next_page_link = next_link
        else:
            next_page_link = None
    return all_quotes


def write_quotes_to_csv(
        quotes: list[Quote],
        authors_cache_dict: dict,
        output_csv_path: str,
        authors_biography_csv_path: str
) -> None:

    with open(output_csv_path, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])

    with open(authors_biography_csv_path, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(AUTHORS_FIELDS)
        writer.writerows(
            [astuple(author) for author in authors_cache_dict.values()]
        )


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(
        get_page_quotes(),
        authors_cache,
        output_csv_path,
        authors_biography_csv_path="authors_biography.csv"
    )


if __name__ == "__main__":
    main("quotes.csv")
