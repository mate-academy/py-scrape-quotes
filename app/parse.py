import csv
from dataclasses import dataclass
import time
from typing import Optional, List, Generator
from urllib.parse import urljoin
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page_content(url: str) -> Optional[str]:
    """
    Fetches the HTML content of a given URL.
    Includes basic error handling for network issues and a small delay.
    """
    try:
        time.sleep(0.5)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_quotes_from_page(html_content: str) -> List[Quote]:
    """
    Parses quotes from the given HTML content
    Extracts text, author, and tags for each quote.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    quotes: List[Quote] = []

    for quote_div in soup.find_all("div", class_="quote"):
        text_element = quote_div.find("span", class_="text")
        text = text_element.get_text(strip=True) if text_element else "N/A"

        author_element = quote_div.find("small", class_="author")
        author = author_element.get_text(
            strip=True
        ) if author_element else "N/A"

        tags_elements_container = quote_div.find("div", class_="tags")
        tags = []
        if tags_elements_container:
            for tag_a in tags_elements_container.find_all("a", class_="tag"):
                tags.append(tag_a.get_text(strip=True))

        quotes.append(Quote(text, author, tags))

    return quotes


def page_generator(start_url: str) -> Generator[BeautifulSoup, None, None]:
    """
    Generates BeautifulSoup objects for each paginated page of the website.
    It automatically follows "Next page" links.
    """
    current_url = start_url
    page_num = 1

    while True:
        print(f"Fetching page {page_num}: {current_url}")
        html_content = fetch_page_content(current_url)

        if not html_content:
            print(
                f"Failed to fetch content for page {page_num}, "
                f"stopping pagination."
            )
            break

        soup = BeautifulSoup(html_content, "html.parser")
        yield soup

        next_li = soup.find("li", class_="next")
        if next_li and next_li.find("a"):
            relative_url = next_li.find("a")["href"]
            current_url = urljoin(start_url, relative_url)
            page_num += 1
        else:
            break


def scrape_all_quotes() -> List[Quote]:
    """
    Orchestrates the scraping of all quotes from the website,
    handling pagination.
    Uses a page generator for efficient processing.
    """
    all_quotes: List[Quote] = []

    for page_soup in tqdm(
            page_generator(BASE_URL),
            desc="Scraping Quotes Pages"
    ):
        quotes_on_page = parse_quotes_from_page(page_soup.prettify())
        all_quotes.extend(quotes_on_page)

    print(f"\nFinished scraping. Total quotes found: {len(all_quotes)}")
    return all_quotes


def write_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    """
    Writes a list of Quote objects to a CSV file.
    """
    if not quotes:
        print(
            "No quotes to write to CSV. "
            "The CSV file will not be created or "
            "will be empty if it already exists."
        )
        return

    fieldnames = ["text", "author", "tags"]
    try:
        with open(
                output_csv_path,
                "w",
                newline="",
                encoding="utf-8"
        ) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for quote in quotes:
                writer.writerow({
                    "text": quote.text,
                    "author": quote.author,
                    # "tags": ", ".join(quote.tags)
                    "tags": quote.tags
                })

        print(f"Successfully wrote {len(quotes)} quotes to {output_csv_path}")
    except IOError as e:
        print(f"Error writing to CSV file {output_csv_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing CSV: {e}")


def main(output_csv_path: str) -> None:
    quotes = scrape_all_quotes()
    if quotes:
        write_quotes_to_csv(quotes, output_csv_path)
    else:
        print(
            "No quotes were scraped. "
            "CSV file will not be created or will be empty."
        )


if __name__ == "__main__":
    main("quotes.csv")
