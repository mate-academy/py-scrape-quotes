from dataclasses import dataclass, astuple

import csv

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


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


cache = {}


def save_author_data_to_cache(author_name: str, author: Author) -> None:
    cache[author_name] = author


def parse_author(author_soup: BeautifulSoup) -> Author:
    author = Author(
        name=author_soup.select_one(".author-title").text,
        born_date=author_soup.select_one(".author-born-date").text,
        born_location=author_soup.select_one(".author-born-location").text,
        description=author_soup.select_one(".author-description").text
    )
    return author


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    single_quote = Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )

    author_name = quote_soup.select_one(".author").text.split()
    slugified_author_name = author_name[0] + "-" + author_name[1]

    if slugified_author_name not in cache:
        author_page = requests.get(
            BASE_URL + f"/author/{slugified_author_name}"
        ).content
        author_soup = BeautifulSoup(author_page, "html.parser")
        author = parse_author(author_soup)
        save_author_data_to_cache(slugified_author_name, author)
    return single_quote


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def check_existing_next_page(page_soup: BeautifulSoup) -> bool:
    next_page = page_soup.select(".next")
    if next_page:
        return True
    return False


def get_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(first_page_soup)

    next_page = check_existing_next_page(first_page_soup)

    counter = 2

    while next_page:
        current_page = requests.get(BASE_URL + f"page/{counter}/").content
        current_soup = BeautifulSoup(current_page, "html.parser")

        next_page = check_existing_next_page(current_soup)

        all_quotes.extend(get_single_page_quotes(current_soup))

        counter += 1
    return all_quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


def write_authors_to_csv() -> None:
    authors = [author for author in cache.values()]
    with open("authors.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(["name", "born_date", "born_location", "description"])
        writer.writerows([astuple(author) for author in authors])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)
    write_authors_to_csv()


if __name__ == "__main__":
    main("quotes.csv")
