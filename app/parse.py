import requests
import csv
from urllib.parse import urljoin
from dataclasses import dataclass, fields, astuple
from datetime import datetime, date
from bs4 import BeautifulSoup, ResultSet, Tag


@dataclass
class AuthorBiography:
    birthday: date
    location: str
    description: str


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"

url_cache = {}


def get_author_biography(url: str) -> AuthorBiography:
    if url not in url_cache:
        author_page = requests.get(urljoin(BASE_URL, url)).content
        soup = BeautifulSoup(author_page, "html.parser")
        birthday = datetime.strptime(
            soup.select_one(".author-born-date").text, "%B %d, %Y"
        ).date()
        location = soup.select_one(".author-born-location").text
        description = soup.select_one(".author-description").text
        author = AuthorBiography(birthday, location, description)
        url_cache[url] = author
        return author
    return url_cache[url]


def get_single_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags = [tag.text for tag in quote.select(".tag")]
    get_author_biography(quote.select_one("span a").get("href"))
    return Quote(text, author, tags)


def get_quotes_on_page(quotes: ResultSet) -> list[Quote]:
    return [get_single_quote(quote) for quote in quotes]


def get_all_quotes() -> list[Quote]:
    quotes_list = []
    first_page = requests.get(BASE_URL).content
    soup = BeautifulSoup(first_page, "html.parser")
    quotes_list += get_quotes_on_page(soup.select(".quote"))
    actual_page = True
    page = 2
    while actual_page:
        next_page = requests.get(urljoin(BASE_URL, f"page/{page}")).content
        soup = BeautifulSoup(next_page, "html.parser")
        quotes = soup.select(".quote")
        if quotes:
            quotes_list += get_quotes_on_page(quotes)
            page += 1
        else:
            actual_page = False
    return quotes_list


def write_csv_file(
        file_name: str,
        title: object,
        all_content: list[object]
) -> None:
    with open(file_name, "w", encoding="utf-8", newline="") as csvfile:
        object_writer = csv.writer(csvfile)
        object_writer.writerow([field.name for field in fields(title)])
        object_writer.writerows([astuple(content) for content in all_content])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_csv_file(output_csv_path, Quote, quotes)
    write_csv_file(
        "authors.csv",
        AuthorBiography,
        [author for author in url_cache.values()]
    )


if __name__ == "__main__":
    main("quotes.csv")
