from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class AuthorBio:
    author: str
    bio: str


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.find(class_="text").get_text()
    author = quote_soup.find(class_="author").get_text()
    tags = [tag.get_text() for tag in quote_soup.find_all(class_="tag")]
    return Quote(text, author, tags)


def get_author_biography(
    author: str, author_bio_url: str, cache: dict
) -> AuthorBio:
    if author_bio_url in cache:
        return cache[author_bio_url]

    response = requests.get(author_bio_url)
    soup = BeautifulSoup(response.content, "html.parser")
    author_bio_element = soup.find(class_="author-description")

    if author_bio_element:
        bio = author_bio_element.get_text(strip=True)
    else:
        bio = "Biography not found"

    author_bio = AuthorBio(author, bio)
    cache[author_bio_url] = author_bio
    return author_bio


def get_all_quotes() -> tuple[list[Quote], list[AuthorBio]]:
    quotes = []
    author_bios = []
    page_number = 1
    author_bio_cache = {}

    while True:
        url = f"{BASE_URL}page/{page_number}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        page_quotes = soup.select(".quote")
        if not page_quotes:
            break

        for quote_soup in page_quotes:
            quote = parse_single_quote(quote_soup)
            author_bio_url = BASE_URL + quote_soup.find("a")["href"]
            author_bio = get_author_biography(
                quote.author, author_bio_url, author_bio_cache
            )
            quotes.append(quote)
            if author_bio not in author_bios:
                author_bios.append(author_bio)

        page_number += 1

    return quotes, author_bios


def save_results_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(
        output_csv_path, mode="w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            tags_str = str(quote.tags).replace('"', "'")
            writer.writerow([quote.text, quote.author, tags_str])


def main(output_csv_path: str) -> None:
    quotes, _ = get_all_quotes()
    save_results_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("result.csv")
