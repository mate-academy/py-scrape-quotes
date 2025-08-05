import requests
from bs4 import BeautifulSoup
import csv
import time
from dataclasses import dataclass
from typing import List, Dict, Optional
from urllib.parse import urljoin


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class AuthorBio:
    name: str
    birth_date: str
    location: str
    description: str


class AuthorBioCache:
    """Cache for author biographies to avoid duplicate requests."""

    def __init__(self) -> None:
        self.cache: Dict[str, AuthorBio] = {}
        self.failed_authors: set = set()

    def get(self, author_name: str) -> Optional[AuthorBio]:
        """Get cached author bio."""
        return self.cache.get(author_name)

    def add(self, author_name: str, bio: AuthorBio) -> None:
        """Add author bio to cache."""
        self.cache[author_name] = bio

    def mark_failed(self, author_name: str) -> None:
        """Mark author as failed to avoid retrying."""
        self.failed_authors.add(author_name)

    def is_failed(self, author_name: str) -> bool:
        """Check if author bio fetch previously failed."""
        return author_name in self.failed_authors


def scrape_author_bio(
        author_url: str,
        author_name: str
) -> Optional[AuthorBio]:
    """
    Scrape author biography from author page.

    Args:
        author_url: URL to the author's page
        author_name: Name of the author

    Returns:
        AuthorBio object or None if scraping fails
    """
    try:
        response = requests.get(author_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        birth_date = ""
        born_span = soup.find("span", class_="author-born-date")
        if born_span:
            birth_date = born_span.get_text(strip=True)

        location = ""
        location_span = soup.find("span", class_="author-born-location")
        if location_span:
            location = location_span.get_text(strip=True)

        description = ""
        description_div = soup.find("div", class_="author-description")
        if description_div:
            description = description_div.get_text(strip=True)

        return AuthorBio(
            name=author_name,
            birth_date=birth_date,
            location=location,
            description=description
        )

    except requests.RequestException as e:
        print(f"Error fetching author bio for {author_name}: {e}")
        return None


def scrape_page_with_bios(url: str, bio_cache: AuthorBioCache) -> List[Quote]:
    """
    Scrape quotes from a single page and collect author bios.

    Args:
        url: The URL of the page to scrape
        bio_cache: Cache for author biographies

    Returns:
        List of Quote objects from the page
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        quotes = []

        quote_divs = soup.find_all("div", class_="quote")

        for quote_div in quote_divs:
            text_span = quote_div.find("span", class_="text")
            if not text_span:
                continue
            text = text_span.get_text(strip=True)

            author_small = quote_div.find("small", class_="author")
            if not author_small:
                continue
            author = author_small.get_text(strip=True)

            tag_links = quote_div.find_all("a", class_="tag")
            tags = [tag.get_text(strip=True) for tag in tag_links]

            quotes.append(Quote(text=text, author=author, tags=tags))

            if not bio_cache.get(author) and not bio_cache.is_failed(author):
                author_link = quote_div.find("a")
                if author_link and author_link.get("href"):
                    author_url = urljoin(url, author_link["href"])
                    print(f"Fetching bio for {author}...")

                    bio = scrape_author_bio(author_url, author)
                    if bio:
                        bio_cache.add(author, bio)
                        print(f"✓ Bio cached for {author}")
                    else:
                        bio_cache.mark_failed(author)
                        print(f"✗ Failed to get bio for {author}")

                    time.sleep(0.5)

        return quotes

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []


def has_next_page(soup: BeautifulSoup) -> bool:
    """
    Check if there's a next page available.

    Args:
        soup: BeautifulSoup object of the current page

    Returns:
        True if next page exists, False otherwise
    """
    next_button = soup.find("li", class_="next")
    return next_button is not None


def scrape_all_quotes_with_bios() -> tuple[List[Quote], AuthorBioCache]:
    """
    Scrape all quotes from all pages of the website along with author bios.

    Returns:
        Tuple of (List of all Quote objects, AuthorBioCache with all bios)
    """
    base_url = "https://quotes.toscrape.com"
    all_quotes = []
    bio_cache = AuthorBioCache()
    page_num = 1

    print("Starting to scrape quotes and author biographies...")

    while True:
        url = f"{base_url}/page/{page_num}/"
        print(f"Scraping page {page_num}...")

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
            break

        soup = BeautifulSoup(response.content, "html.parser")

        quote_divs = soup.find_all("div", class_="quote")
        if not quote_divs:
            print(f"No quotes found on page {page_num}. Ending scrape.")
            break

        page_quotes = scrape_page_with_bios(url, bio_cache)
        all_quotes.extend(page_quotes)

        print(f"Found {len(page_quotes)} quotes on page {page_num}")

        if not has_next_page(soup):
            print("No more pages found. Scraping complete.")
            break

        page_num += 1

        time.sleep(0.5)

    print(f"Total quotes scraped: {len(all_quotes)}")
    print(f"Total author bios collected: {len(bio_cache.cache)}")
    return all_quotes, bio_cache


def save_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    """
    Save quotes to a CSV file.

    Args:
        quotes: List of Quote objects to save
        output_csv_path: Path to the output CSV file
    """
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for quote in quotes:
            writer.writerow({
                "text": quote.text,
                "author": quote.author,
                "tags": str(quote.tags)
            })

    print(f"Quotes saved to {output_csv_path}")


def save_author_bios_to_csv(
        bio_cache: AuthorBioCache,
        output_csv_path: str
) -> None:
    """
    Save author biographies to a CSV file.

    Args:
        bio_cache: AuthorBioCache containing all author bios
        output_csv_path: Path to the output CSV file
    """
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["name", "birth_date", "location", "description"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for bio in bio_cache.cache.values():
            writer.writerow({
                "name": bio.name,
                "birth_date": bio.birth_date,
                "location": bio.location,
                "description": bio.description
            })

    print(f"Author biographies saved to {output_csv_path}")


def main(quotes_csv_path: str = "quotes.csv",
         authors_csv_path: str = "authors.csv") -> None:
    """
    Main function to scrape all quotes and author bios,
    saving them to separate CSV files.

    Args:
        quotes_csv_path: Path to the quotes CSV file
        authors_csv_path: Path to the authors CSV file
    """
    try:
        all_quotes, bio_cache = scrape_all_quotes_with_bios()

        if not all_quotes:
            print(
                "No quotes were scraped. Please check the website structure."
            )
            return

        save_quotes_to_csv(all_quotes, quotes_csv_path)

        save_author_bios_to_csv(bio_cache, authors_csv_path)

        print(f"Successfully scraped {len(all_quotes)} quotes "
              f"and {len(bio_cache.cache)} author biographies")
        print(f"Quotes saved to: {quotes_csv_path}")
        print(f"Author bios saved to: {authors_csv_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
