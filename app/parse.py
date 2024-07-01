from dataclasses import dataclass
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import csv
import logging

BASE_URL = "https://quotes.toscrape.com/"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


@dataclass
class Author:
    name: str
    bio: str


OUTPUT_QUOTES_PATH = "quotes.csv"
OUTPUT_AUTHORS_PATH = "authors.csv"


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = [tag.get_text(strip=True) for tag in quote_soup.select(".tag")]
    logging.debug(f"Parsed quote: {text} by {author} with tags {tags}")
    return Quote(text=text, author=author, tags=tags)


def parse_author_bio(author_url: str) -> Author:
    logging.info(f"Fetching bio for author from {BASE_URL + author_url}")
    author_page = requests.get(BASE_URL + author_url).content
    author_soup = BeautifulSoup(author_page, "html.parser")
    name = author_soup.select_one(".author-title").text.strip()
    bio = author_soup.select_one(".author-description").text.strip()
    logging.debug(f"Parsed author: {name} with bio {bio}")
    return Author(name=name, bio=bio)


def get_single_page_quotes(
        page_soup: BeautifulSoup,
        authors: Dict[str, Author]
) -> List[Quote]:
    quotes = page_soup.select(".quote")
    quotes_list = []
    for quote_soup in quotes:
        quote = parse_single_quote(quote_soup)
        author_url = quote_soup.select_one("a")["href"]
        if quote.author not in authors:
            logging.info(f"Fetching bio for new author: {quote.author}")
            authors[quote.author] = parse_author_bio(author_url)
        quotes_list.append(quote)
    return quotes_list


def get_all_quotes_and_authors() -> (List[Quote], Dict[str, Author]):
    logging.info("Starting to scrape all quotes and authors")
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    all_quotes = []
    authors = {}

    all_quotes.extend(get_single_page_quotes(soup, authors))

    next_button = soup.select_one("li.next > a")
    while next_button:
        next_page_url = BASE_URL + next_button["href"]
        logging.info(f"Fetching quotes from page {next_page_url}")
        page = requests.get(next_page_url).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup, authors))
        next_button = soup.select_one("li.next > a")

    logging.info("Finished scraping all quotes and authors")
    return all_quotes, authors


def save_to_csv(
        data: List[Dict[str, Any]],
        headers: List[str],
        output_csv_path: str
) -> None:
    logging.info(f"Saving data to {output_csv_path}")
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for item in data:
            writer.writerow(item)
            logging.debug(f"Saved item: {item}")
    logging.info(f"Data saved to {output_csv_path}")


def save_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    data = [
        {
            "text": quote.text,
            "author": quote.author,
            "tags": quote.tags
        } for quote in quotes
    ]
    headers = ["text", "author", "tags"]
    save_to_csv(data, headers, output_csv_path)


def save_authors_to_csv(
        authors: Dict[str, Author],
        output_csv_path: str
) -> None:
    data = [
        {
            "name": author.name,
            "bio": author.bio
        } for author in authors.values()
    ]
    headers = ["name", "bio"]
    save_to_csv(data, headers, output_csv_path)


def main(output_quotes_csv_path: str) -> None:
    quotes, authors = get_all_quotes_and_authors()
    save_quotes_to_csv(quotes, output_quotes_csv_path)
    save_authors_to_csv(authors, OUTPUT_AUTHORS_PATH)
    logging.info("Quotes and authors saved successfully")


if __name__ == "__main__":
    main(OUTPUT_QUOTES_PATH)
