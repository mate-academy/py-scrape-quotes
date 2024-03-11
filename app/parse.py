import csv
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]
    bio: str | None = None


def parse_single_quote(quote_element: BeautifulSoup) -> Quote:
    text = quote_element.select_one(".text").text.strip()
    author = quote_element.select_one(".author").text.strip()
    tags = [tag.text for tag in quote_element.select(".tags .tag")]
    bio = get_author_bio(quote_element.find("a"
                                            )["href"])
    return Quote(text, author, tags, bio)


def get_author_bio(author_url: str) -> str:
    bio_content = requests.get(BASE_URL + author_url).content
    bio_soup = BeautifulSoup(bio_content, "html.parser")
    bio_text = bio_soup.select_one(".author-description"
                                   ).text.strip()
    return bio_text


def parse_quotes() -> List[Quote]:
    all_quotes = []
    page_number = 1
    while True:
        page_url = f"{BASE_URL}page/{page_number}/"
        page = requests.get(page_url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = soup.select(".quote")
        if not quotes:
            break  # No more quotes, break out of the loop
        all_quotes.extend([parse_single_quote(quote) for quote in quotes])
        page_number += 1
    return all_quotes


def write_quotes_to_csv(quotes: List[Quote],
                        output_csv_path: str,
                        ) -> None:
    fieldnames = ["text", "author", "tags", "bio"]
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for quote in quotes:
            writer.writerow(
                {"text": quote.text,
                 "author": quote.author,
                 "tags": quote.tags,
                 "bio": quote.bio},
            )


def main(output_csv_path: str, ) -> None:
    quotes = parse_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("my_quotes.csv")
