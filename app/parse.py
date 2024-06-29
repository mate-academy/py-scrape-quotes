import csv
from dataclasses import dataclass, astuple
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


@dataclass
class Author:
    name: str
    born_date: str
    born_location: str
    description: str


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    """Parse a single quote from the BeautifulSoup object."""
    tags_content = quote_soup.select_one(".keywords")["content"]
    tags = tags_content.split(",") if tags_content else []
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=tags,
    )


def parse_author(author_soup: BeautifulSoup) -> Author:
    """Parse an author from the BeautifulSoup object."""
    return Author(
        name=author_soup.select_one(".author-title").text,
        born_date=author_soup.select_one(".author-born-date").text,
        born_location=author_soup.select_one(
            ".author-born-location"
        ).text[3:],
        description=author_soup.select_one(".author-description").text,
    )


def fetch_html(url: str) -> BeautifulSoup:
    response = requests.get(url)
    return BeautifulSoup(response.content, "html.parser")


def get_author_bio(author_page: str) -> Author:
    """Fetch and parse author biography from the given URL."""
    try:
        soup = fetch_html(author_page)
        author_soup = soup.select_one(".author-details")
        return parse_author(author_soup)

    except (requests.RequestException, AttributeError) as e:
        print(f"Error fetching author bio from {author_page}: {e}")
        return Author(name="", born_date="", born_location="", description="")


def get_next_page(current_url: str) -> Optional[str]:
    """Get the URL of the next page if it exists."""
    try:
        soup = fetch_html(current_url)
        next_link = soup.select_one("li.next a")
        if next_link:
            next_page_url = next_link["href"]
            return f"{BASE_URL.rstrip('/')}{next_page_url}"  # noqa: Q000
        return None
    except requests.RequestException as e:
        print(f"Error fetching next page from {current_url}: {e}")
        return None


def get_single_page_quotes(page_url: str) -> List[Quote]:
    """Fetch and parse quotes from a single page."""
    try:
        soup = fetch_html(page_url)
        quotes = soup.select(".quote")
        return [parse_single_quote(quote_soup) for quote_soup in quotes]
    except requests.RequestException as e:
        print(f"Error fetching quotes from {page_url}: {e}")
        return []


def get_all_quotes() -> List[Quote]:
    """Fetch all quotes by iterating through pages."""
    all_quotes = []
    current_url = BASE_URL

    while current_url:
        quotes = get_single_page_quotes(current_url)
        all_quotes.extend(quotes)
        current_url = get_next_page(current_url)

    return all_quotes


def get_authors_bio() -> List[Author]:
    """Fetch and cache author biographies."""
    authors_bio: Dict[str, Author] = {}
    quotes = get_all_quotes()

    for quote in quotes:
        author_name = quote.author
        if author_name not in authors_bio:
            fixed_name = "-".join(
                name if name.isalpha() else name[:-1]
                for name in author_name.split()
            )
            author_bio = get_author_bio(f"{BASE_URL}/author/{fixed_name}/")
            authors_bio[author_name] = author_bio

    return list(authors_bio.values())


def write_authors_bio_to_file(output_csv_path: str) -> None:
    """Write author biographies to a CSV file."""
    authors_bio = get_authors_bio()
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["name", "born_date", "born_location", "description"])
        writer.writerows([astuple(author) for author in authors_bio])


def main(output_csv_path: str) -> None:
    """Write quotes to a CSV file."""
    quotes = get_all_quotes()
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
    write_authors_bio_to_file("authors.csv")
