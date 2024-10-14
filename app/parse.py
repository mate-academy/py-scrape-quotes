import csv
import requests
from dataclasses import dataclass, fields
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    full_name: str
    birth_date: str
    description: str


author_cache = {}


def cache_author_bio(author_url: str) -> Author:
    if author_url in author_cache:
        return author_cache[author_url]

    page = requests.get(author_url).content
    soup = BeautifulSoup(page, "html.parser")

    author = parse_single_author(soup)

    author_cache[author_url] = author

    return author


def parse_single_author(author_soup: BeautifulSoup) -> Author:
    author_title = author_soup.select_one(".author-title").text.strip()
    birth_date = author_soup.select_one(".author-born-date").text.strip()
    description = author_soup.select_one(".author-description").text.strip()

    return Author(
        full_name=author_title,
        birth_date=birth_date,
        description=description
    )


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = [tag.text for tag in quote_soup.select(".tag")]

    author_info = quote_soup.select_one("a[href^='/author/']")["href"]
    author_url = BASE_URL + author_info

    cache_author_bio(author_url)

    return Quote(text=text, author=author, tags=tags)


def get_pages() -> int:
    pages = 2
    while True:
        page_url = f"{BASE_URL}/page/{pages}/"

        page_content = requests.get(page_url).content

        soup = BeautifulSoup(page_content, "html.parser")

        next_page = soup.select_one(".next a")
        if not next_page:
            pages += 1
            break

        pages += 1

    return pages - 1


def get_single_page_quote(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    num_pages = get_pages()

    all_quotes = get_single_page_quote(first_page_soup)

    for page_num in range(2, num_pages + 1):
        page = requests.get(f"{BASE_URL}/page/{page_num}/").content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quote(soup))

    return all_quotes


def write_quotes(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def write_authors(output_csv_path: str, authors: dict) -> None:
    with open(output_csv_path, "w", encoding="utf8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Author)])
        for author in authors.values():
            writer.writerow(
                [author.full_name, author.birth_date, author.description]
            )


def main(output_csv_quotes_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes(output_csv_quotes_path, quotes)


def author(output_csv_authors_path: str) -> None:
    write_authors(output_csv_authors_path, author_cache)


if __name__ == "__main__":
    main("quotes.csv")
    author("authors.csv")
