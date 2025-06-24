from dataclasses import dataclass
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import csv
import time


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


@dataclass
class Author:
    name: str
    birth_date: str
    birth_location: str
    description: str


BASE_URL = "http://quotes.toscrape.com"


def parse_single_quote(tag) -> Quote:
    text = tag.select_one(".text").text.strip("“”")
    author = tag.select_one(".author").text
    tags = [t.text for t in tag.select(".tags .tag")]
    return Quote(text=text, author=author, tags=tags)


def parse_author_info(author_url: str) -> Author:
    response = requests.get(BASE_URL + author_url)
    soup = BeautifulSoup(response.content, "html.parser")

    name = soup.select_one("h3.author-title").text.strip()
    birth_date = soup.select_one(".author-born-date").text.strip()
    birth_location = soup.select_one(".author-born-location").text.strip("in ")
    description = soup.select_one(".author-description").text.strip()

    return Author(name=name, birth_date=birth_date, birth_location=birth_location, description=description)


def get_all_quotes_and_authors():
    quotes = []
    authors: Dict[str, Author] = {}
    page = 1

    while True:
        url = f"{BASE_URL}/page/{page}/"
        response = requests.get(url)
        if "No quotes found!" in response.text:
            break

        soup = BeautifulSoup(response.content, "html.parser")
        quote_tags = soup.select(".quote")

        for tag in quote_tags:
            quote = parse_single_quote(tag)
            quotes.append(quote)

            author_name = quote.author
            if author_name not in authors:
                author_url = tag.select_one("span a")["href"]
                authors[author_name] = parse_author_info(author_url)
                time.sleep(0.5)

        page += 1
        time.sleep(1)

    return quotes, list(authors.values())


def save_quotes_to_csv(quotes: List[Quote], output_path: str):
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, ", ".join(quote.tags)])


def save_authors_to_csv(authors: List[Author], output_path: str):
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "birth_date", "birth_location", "description"])
        for author in authors:
            writer.writerow([author.name, author.birth_date, author.birth_location, author.description])


def main(output_csv_path: str) -> None:
    quotes, authors = get_all_quotes_and_authors()
    save_quotes_to_csv(quotes, output_csv_path)
    save_authors_to_csv(authors, "authors.csv")


if __name__ == "__main__":
    main("quotes.csv")
