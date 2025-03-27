from bs4 import BeautifulSoup, Tag
import requests

from dataclasses import dataclass, fields
from urllib.parse import urljoin
import csv

BASE_URL = "https://quotes.toscrape.com/"
AUTHORS_CACHE = set()


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
    bio: str


def parse_article(soup_article: Tag) -> Quote:
    soup_tags = soup_article.select(".tag")
    tags = [tag.text for tag in soup_tags]
    return Quote(
        text=soup_article.select_one(".text").text,
        author=soup_article.select_one(".author").text,
        tags=tags
    )


def parse_author(path_author: str) -> Author:
    url = urljoin(BASE_URL, path_author)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    autor_title = soup.select_one(".author-title").text
    AUTHORS_CACHE.add(autor_title)
    return Author(
        name=autor_title,
        born_date=soup.select_one(".author-born-date").text,
        born_location=soup.select_one(
            ".author-born-location").text.replace("in ", ""),
        bio=soup.select_one(".author-description").text.strip()
    )


def parse_page(url: str) -> tuple[list[Quote], list[Author]]:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    quotes = soup.select(".quote")

    all_article = []
    all_authors = []

    for quote in quotes:
        article = parse_article(quote)
        all_article.append(article)

        if article.author not in AUTHORS_CACHE:
            path_author = quote.select_one("a")["href"]
            author_bio = parse_author(path_author)
            all_authors.append(author_bio)

    return all_article, all_authors


def next_page_tag(url: str) -> Tag:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup.select_one(".next")


def parse_pages() -> tuple[list[Quote], list[Author]]:
    articles, authors = parse_page(BASE_URL)
    next_page = next_page_tag(BASE_URL)

    while next_page:
        page = next_page.select_one("[href]")["href"]
        url_page = urljoin(BASE_URL, page)
        articles_and_authors = parse_page(url_page)
        articles.extend(articles_and_authors[0])
        authors.extend(articles_and_authors[1])
        next_page = next_page_tag(url_page)

    return articles, authors


def save_quotes_csv(file_name: str, objects: list) -> None:
    if not objects:
        return

    field_names = [field.name for field in fields(objects[0].__class__)]

    with open(file_name, "w", encoding="UTF-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(field_names)

        for obj in objects:
            writer.writerow([getattr(obj, field) for field in field_names])


def main(*output_csv_path) -> None:
    articles, authors = parse_pages()
    save_quotes_csv(output_csv_path[0], articles)

    if len(output_csv_path) > 1:
        save_quotes_csv(output_csv_path[1], authors)


if __name__ == "__main__":
    main("quotes.csv", "authors.csv")
