import csv
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
AUTHOR_CACHE: Dict[str, str] = {}


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


def get_quotes_from_page(url: str) -> (
        Tuple)[List[Dict[str, str]], Optional[str]]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    quotes_data: List[Dict[str, str]] = []
    for quote in soup.select(".quote"):
        text = quote.select_one(".text").get_text(strip=True)
        author = quote.select_one(".author").get_text(strip=True)
        author_url = BASE_URL + quote.select_one("a")["href"]
        tags = [tag.get_text(strip=True) for tag in quote.select(".tag")]
        quotes_data.append({
            "text": text,
            "author": author,
            "author_url": author_url,
            "tags": tags,
        })
    next_btn = soup.select_one(".pager .next a")
    next_page = BASE_URL + next_btn["href"] if next_btn else None
    return quotes_data, next_page


def get_author_bio(url: str) -> str:
    if url in AUTHOR_CACHE:
        return AUTHOR_CACHE[url]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    bio: str = soup.select_one(".author-description").get_text(strip=True)
    AUTHOR_CACHE[url] = bio
    return bio


def save_to_csv(
        file_path: str, fieldnames: List[str], data: List[Dict[str, str]]
) -> None:
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def main(
        output_quotes_csv: str,
        output_authors_csv: Optional[str] = None
) -> None:
    all_quotes: List[Dict[str, str]] = []
    all_authors: List[Dict[str, str]] = []

    next_page_url: Optional[str] = BASE_URL
    while next_page_url:
        quotes, next_page_url = get_quotes_from_page(next_page_url)
        for quote in quotes:
            all_quotes.append(
                {
                    "text": quote["text"],
                    "author": quote["author"],
                    "tags": quote["tags"],
                }
            )
            if output_authors_csv:
                bio: str = get_author_bio(quote["author_url"])
                all_authors.append({"author": quote["author"], "bio": bio})

    save_to_csv(output_quotes_csv, ["text", "author", "tags"], all_quotes)

    if output_authors_csv:
        save_to_csv(output_authors_csv, ["author", "bio"], all_authors)


if __name__ == "__main__":
    main("output_quotes_csv")
