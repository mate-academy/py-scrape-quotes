import csv
from dataclasses import dataclass, fields
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Author:
    name: str
    biography: str


@dataclass
class Quote:
    text: str
    author: Author
    tags: list[str]


def get_quote(content: Tag, authors: list[Author]) -> Quote:
    tags_html = content.select(".tag")
    author_name = content.select_one(".author").text
    if not any(author_name == author.name for author in authors):
        author_link = content.select_one("span.author + a")
        link_to_biography = urljoin(BASE_URL, author_link["href"])
        text = requests.get(link_to_biography).content
        biography = (BeautifulSoup(text, "html.parser")
                     .select_one(".author-description").text)
        author = Author(name=author_name, biography=biography)
    else:
        author = next((author_obj
                       for author_obj in authors
                       if author_name == author_obj.name), None)
    return Quote(
        text=content.select_one(".text").text,
        author=author,
        tags=[tag.text for tag in tags_html]
    )


def get_quotes_list(link: str,
                    authors: list[Author]) -> tuple[list[Quote], Tag]:
    text = requests.get(link).content
    soup = BeautifulSoup(text, "html.parser")
    quotes_html = soup.select(".quote")
    pagination = soup.select_one(".next a")
    return [get_quote(quote_block, authors)
            for quote_block in quotes_html], pagination


def main(output_csv_path: str) -> None:
    authors = []
    quotes, pagination = get_quotes_list(BASE_URL, authors)
    while pagination:
        next_page = urljoin(BASE_URL, pagination["href"])
        parsed_quotes, pagination = get_quotes_list(next_page, authors)
        quotes.extend(parsed_quotes)
    with open(output_csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow([field.name for field in fields(Quote)])
        writer.writerows([(quote.text,
                           quote.author.name,
                           quote.author.biography,
                           ",".join(quote.tags)) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
