import csv
import os
import time
import urllib.parse
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_soup(url: str) -> BeautifulSoup | None:
    """Safely fetch HTML content and return a BeautifulSoup object."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
        print(f"Failed to fetch {url}: Status code {response.status_code}")
    except requests.RequestException as e:
        print(f"Network error while fetching {url}: {e}")
    return None


def parse_author_bio(author_url: str) -> str:
    """Extract the author's biography text from their detail page."""
    soup = get_soup(author_url)
    if not soup:
        return ""

    bio_element = soup.find("div", class_="author-description")
    return bio_element.text.strip() if bio_element else ""


def parse_single_page(
    soup: BeautifulSoup, authors_cache: dict
) -> list[tuple[Quote, str]]:
    """Extract quote instances and return pairs of (Quote, author_bio)."""
    page_data = []
    quote_elements = soup.find_all("div", class_="quote")

    for element in quote_elements:
        text = element.find("span", class_="text").text.strip()
        author_name = element.find("small", class_="author").text.strip()

        tag_elements = element.find_all("a", class_="tag")
        tags = [tag.text.strip() for tag in tag_elements]

        quote_obj = Quote(text=text, author=author_name, tags=tags)

        author_link_element = element.find("a", string="(about)")
        bio = ""

        if author_link_element:
            rel_author_url = author_link_element["href"]
            abs_author_url = urllib.parse.urljoin(BASE_URL, rel_author_url)

            if abs_author_url not in authors_cache:
                print(f"Scraping bio for new author: {author_name}")
                authors_cache[abs_author_url] = parse_author_bio(
                    abs_author_url
                )
                time.sleep(0.5)

            bio = authors_cache[abs_author_url]

        page_data.append((quote_obj, bio))

    return page_data


def main(output_csv_path: str) -> None:
    """Traverse all pages, extract quotes, and write them to a CSV file."""
    all_records = []
    authors_cache = {}  # Format: {author_url: bio_text}
    current_url = BASE_URL

    print("Starting quote scraper pipeline...")

    while current_url:
        print(f"Scraping page: {current_url}")
        soup = get_soup(current_url)

        if not soup:
            break

        records_from_page = parse_single_page(soup, authors_cache)
        all_records.extend(records_from_page)

        next_button = soup.find("li", class_="next")
        if next_button:
            next_page_url = next_button.find("a")["href"]
            current_url = urllib.parse.urljoin(BASE_URL, next_page_url)
            time.sleep(0.5)
        else:
            current_url = None

    dir_name = os.path.dirname(output_csv_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote_obj, bio in all_records:
            tags_serialized = str(quote_obj.tags)
            writer.writerow(
                [
                    quote_obj.text,
                    quote_obj.author,
                    tags_serialized
                ]
            )

    print(
        f"Pipeline complete! {len(all_records)} "
        f"instances written to: {output_csv_path}"
    )


if __name__ == "__main__":
    main("quotes.csv")
