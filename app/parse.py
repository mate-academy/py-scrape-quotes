import csv
from dataclasses import dataclass, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Author:
    title: str
    born: str
    description: str


def parse_single_author(author: Tag) -> Author:
    born_date = author.select_one(".author-born-date").text
    born_location = author.select_one(".author-born-location").text
    return Author(
        title=author.select_one(".author-title").text,
        born=f"{born_date} {born_location}",
        description=author.select_one(".author-description").text,
    )


def get_author_details(author_relative_url: str) -> Author:
    full_url = urljoin(BASE_URL, author_relative_url)
    print(f"Scraping Author: {full_url}")
    response = requests.get(full_url).content
    soup = BeautifulSoup(response, "html.parser")
    author_details = soup.select_one(".author-details")
    return parse_single_author(author_details)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tags .tag")],
    )


def get_quotes_and_authors_urls() -> tuple[list[Quote], set[str]]:
    all_quotes = []
    author_urls = set()
    current_url = BASE_URL

    while current_url:
        print(f"Scraping: {current_url}")

        response = requests.get(current_url).content
        soup = BeautifulSoup(response, "html.parser")
        quotes_elements = soup.select(".quote")

        for quote_el in quotes_elements:
            all_quotes.append(parse_single_quote(quote_el))
            author_link = quote_el.select_one("span a")["href"]
            author_urls.add(author_link)

        next_btn = soup.select_one("li.next > a")

        if next_btn:
            next_link = next_btn["href"]
            current_url = urljoin(BASE_URL, next_link)
        else:
            current_url = None

    return all_quotes, author_urls


def main(output_csv_path: str) -> None:
    quotes, author_urls_set = get_quotes_and_authors_urls()
    with open(output_csv_path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])

    authors_data = []
    for url in author_urls_set:
        authors_data.append(get_author_details(url))

    with open("authors.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["title", "born", "description"])
        writer.writerows([astuple(author) for author in authors_data])


if __name__ == "__main__":
    main("quotes.csv")
