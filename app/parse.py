import csv
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_quotes(soup: BeautifulSoup) -> list[Quote]:
    quotes = []

    for quote_block in soup.select(".quote"):
        text = quote_block.select_one(".text").get_text()
        author = quote_block.select_one(".author").get_text()
        tags = [tag.get_text() for tag in quote_block.select(".tag")]

        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def get_next_page(soup: BeautifulSoup) -> str | None:
    next_btn = soup.select_one(".next a")
    if next_btn:
        return BASE_URL + next_btn["href"]
    return None


def fetch_author_bio(author_url: str, cache: dict) -> str:
    if author_url in cache:
        return cache[author_url]

    soup = fetch_page(author_url)
    bio = soup.select_one(".author-description").get_text().strip()
    cache[author_url] = bio
    return bio


def save_to_csv(quotes: list[Quote], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, ", ".join(quote.tags)])


def main(output_csv_path: str) -> None:
    url = BASE_URL
    all_quotes = []
    author_cache = {}

    while url:
        soup = fetch_page(url)

        quotes = parse_quotes(soup)
        for quote_block, quote in zip(soup.select(".quote"), quotes):
            author_link = quote_block.select_one("a")["href"]
            full_url = BASE_URL + author_link

            fetch_author_bio(full_url, author_cache)

        all_quotes.extend(quotes)

        url = get_next_page(soup)

    save_to_csv(all_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
