import requests
import csv
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dataclasses import dataclass
from typing import List, Dict

# ---------------------------------------------------------------------------
# Mocking the structure assumed to be in app/parse.py
# In a real project, you would import this: from app.parse import Quote
# ---------------------------------------------------------------------------
@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]

# ---------------------------------------------------------------------------
# Scraper Implementation
# ---------------------------------------------------------------------------

BASE_URL = "https://quotes.toscrape.com"

def get_soup(url: str) -> BeautifulSoup:
    """Helper to fetch a page and return a BeautifulSoup object."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_author_bio(bio_relative_url: str, cache: Dict[str, str]) -> str:
    """
    Scrapes the author's biography given a relative URL.
    Uses a cache dictionary to avoid redundant requests.
    """
    if bio_relative_url in cache:
        return cache[bio_relative_url]

    full_url = urljoin(BASE_URL, bio_relative_url)
    soup = get_soup(full_url)
    
    if soup:
        # Assuming the bio is in a div with class 'author-description'
        bio_text = soup.select_one(".author-description")
        if bio_text:
            text = bio_text.get_text(strip=True)
            cache[bio_relative_url] = text
            time.sleep(0.5) # Be gentle to the server
            return text
    
    return ""

def main(output_csv_path: str):
    quotes_data: List[Quote] = []
    author_bio_cache: Dict[str, str] = {}
    
    current_page = "/page/1/"
    
    print("Starting scrape...")

    while current_page:
        url = urljoin(BASE_URL, current_page)
        print(f"Scraping page: {url}")
        
        soup = get_soup(url)
        if not soup:
            break

        # Find all quote blocks
        quote_blocks = soup.select(".quote")
        
        for block in quote_blocks:
            # 1. Extract Text
            text = block.select_one(".text").get_text(strip=True)
            
            # 2. Extract Author
            author_name = block.select_one(".author").get_text(strip=True)
            
            # 3. Extract Tags
            tags = [tag.get_text(strip=True) for tag in block.select(".tag")]
            
            # Add to list
            quotes_data.append(Quote(text, author_name, tags))

            # --- Optional Task: Collect Author Biography ---
            # Find the (about) link usually located next to the author name
            about_link = block.select_one("a[href*='/author/']")
            if about_link:
                bio_url = about_link['href']
                # We scrape the bio now to populate the cache
                scrape_author_bio(bio_url, author_bio_cache)

        # Find 'Next' button
        next_li = soup.select_one("li.next a")
        if next_li:
            current_page = next_li["href"]
            time.sleep(0.5) # Be gentle between pages
        else:
            current_page = None

    # Write Quotes to CSV
    print(f"Writing {len(quotes_data)} quotes to {output_csv_path}...")
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes_data:
            # Joining tags with a semicolon for CSV storage
            writer.writerow([quote.text, quote.author, ";".join(quote.tags)])

    # Write Biographies to a separate CSV (Optional Task)
    authors_csv_path = "authors.csv"
    print(f"Writing {len(author_bio_cache)} author biographies to {authors_csv_path}...")
    with open(authors_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["author_url", "biography"])
        for url, bio in author_bio_cache.items():
            writer.writerow([url, bio])

    print("Done.")

if __name__ == "__main__":
    main("quotes.csv")
