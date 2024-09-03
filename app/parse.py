import csv
from dataclasses import dataclass, fields
import requests
from bs4 import BeautifulSoup


URL = "https://quotes.toscrape.com/"
QUOTE_OUTPUT_CSV_PATH = "result.csv"
AUTHORS_OUTPUT_CSV_PATH = "authors.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    author_name: str
    birth_date: str
    place_of_birth: str
    description: str


def parse_single_author(author: BeautifulSoup) -> Author:
    return Author(
        author_name=author.select_one(".author-title").text,
        birth_date=author.select_one(".author-born-date").text,
        place_of_birth=author.select_one(".author-born-location").text,
        description=author.select_one(".author-description").text
    )


def parse_single_quote(quote: BeautifulSoup) -> (Quote, str):
    author_href = quote.select_one(".author").find_next_sibling("a")["href"]
    author_url = URL + author_href
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    ), author_url


def get_list_quotes(soup: BeautifulSoup) -> list[Quote]:
    all_quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in all_quotes]


def get_author_details(
        author_name: str,
        author_url: str,
        cache: dict
) -> Author:
    if author_name not in cache:
        page_author = requests.get(author_url).content
        soup = BeautifulSoup(page_author, "html.parser")
        author = parse_single_author(soup)
        cache[author_name] = author

        return cache[author_name]


def get_page_number() -> int:
    url = URL
    page_number = 1

    while True:
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        next_button = soup.select_one(".next > a")
        if next_button:
            page_number += 1
            url = URL + next_button["href"]
        else:
            break
    return page_number


def get_quotes(cache: dict) -> list[Quote]:
    all_quotes = []
    page_numbers = get_page_number()

    for page_num in range(1, page_numbers + 1):
        page = requests.get(URL + f"/page/{page_num}/").content
        soup = BeautifulSoup(page, "html.parser")
        quotes_on_page = get_list_quotes(soup)
        all_quotes.extend(quote for quote, _ in quotes_on_page)

        for quote, author_url in quotes_on_page:
            get_author_details(quote.author, author_url, cache)
    return all_quotes


def write_quites_to_csv(quotes: list[Quote]) -> None:
    with open(QUOTE_OUTPUT_CSV_PATH, "w", encoding="utf8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def write_authors_to_csv(authors: list[Author]) -> None:
    with open(
            AUTHORS_OUTPUT_CSV_PATH,
            "w", encoding="utf8", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Author)])
        for author in authors:
            writer.writerow([
                author.author_name,
                author.birth_date,
                author.place_of_birth,
                author.description
            ])


def get_all_authors_from_csv() -> dict:
    authors = {}
    try:
        with open(
                AUTHORS_OUTPUT_CSV_PATH,
                "r", encoding="utf8", newline=""
        ) as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                author = Author(
                    author_name=row["author_name"],
                    birth_date=row["birth_date"],
                    place_of_birth=row["place_of_birth"],
                    description=row["description"]
                )
                authors[author.author_name] = author
    except FileNotFoundError:
        pass
    return authors


def main(output_csv_path: str) -> None:
    cache_author = get_all_authors_from_csv()
    quotes = get_quotes(cache_author)

    write_quites_to_csv(quotes)

    authors_list = list(cache_author.values())
    write_authors_to_csv(authors_list)


if __name__ == "__main__":
    main("result.csv")
