from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import csv
import time
from pathlib import Path


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    birth_date: str
    birth_location: str
    description: str


def get_quotes_from_page(url: str) -> tuple[list[Quote], Optional[str], list[str]]:
    """Gets quotes from one page and returns the next page URL and author links."""
    response = requests.get(url, timeout=5)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    quotes_data: list[Quote] = []
    author_links: list[str] = []

    for quote_div in soup.select(".quote"):
        text_tag = quote_div.select_one(".text")
        author_tag = quote_div.select_one(".author")
        author_link_tag = quote_div.select_one("a[href*='/author/']")

        if not (text_tag and author_tag and author_link_tag):
            continue

        text = text_tag.get_text(strip=True)
        author = author_tag.get_text(strip=True)
        tags = [t.get_text(strip=True) for t in quote_div.select(".tag")]
        author_url = urljoin(BASE_URL, author_link_tag['href'])
        author_links.append(author_url)

        quotes_data.append(Quote(text=text, author=author, tags=tags))

    next_btn = soup.select_one(".next > a")
    next_url = urljoin(BASE_URL, next_btn['href']) if next_btn else None

    return quotes_data, next_url, author_links


def get_author_info(url: str) -> Author:
    """Parses the author page and returns data."""
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    def safe_get(selector: str) -> str:
        tag = soup.select_one(selector)
        if tag:
            return tag.get_text(strip=True)
        else:
            print(f"⚠ Warning: Missing field '{selector}' at {url}")
            return ""

    name = safe_get(".author-title")
    birth_date = safe_get(".author-born-date")
    birth_location = safe_get(".author-born-location")
    description = safe_get(".author-description")

    return Author(name, birth_date, birth_location, description)


def main(output_csv_path: str) -> None:
    url = BASE_URL
    all_quotes = []
    authors_cache = {}

    output_csv_path = Path(output_csv_path)
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    authors_csv_path = output_csv_path.parent / "authors.csv"

    while url:
        current_page = url  # save the current page
        quotes, url, author_links = get_quotes_from_page(url)
        all_quotes.extend(quotes)

        for author_link in set(author_links):
            if author_link not in authors_cache:
                try:
                    author = get_author_info(author_link)
                except requests.RequestException as e:
                    print(f"⚠ Network error while parsing {author_link}: {e}")
                    author = Author(name="", birth_date="", birth_location="", description="")
                except Exception as e:
                    print(f"⚠ Parsing error for {author_link}: {e}")
                    author = Author(name="", birth_date="", birth_location="", description="")

                authors_cache[author_link] = author
                time.sleep(0.05)

        print(f"✅ Parsed page: {current_page}")  # print the correct page

    # Recording quotes
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])
        for q in all_quotes:
            writer.writerow([q.text, q.author, ", ".join(q.tags)])

    # Authors record
    with open(authors_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["name", "birth_date", "birth_location", "description"])
        for author in authors_cache.values():
            writer.writerow([
                author.name,
                author.birth_date,
                author.birth_location,
                author.description
            ])

    print(f"✅ Parsed {len(all_quotes)} quotes and {len(authors_cache)} authors.")
