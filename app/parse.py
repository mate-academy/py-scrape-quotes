from dataclasses import dataclass
from typing import Iterable, List
from urllib.parse import urljoin
import csv
import time

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"


def _session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    })
    return session


def _get_soup(
        url: str,
        session: requests.Session,
        sleep_after: float = 0.25
) -> BeautifulSoup:
    """Fetch a URL and return BeautifulSoup; small sleep to be gentle."""
    resp = session.get(url, timeout=15)
    resp.raise_for_status()
    time.sleep(sleep_after)
    return BeautifulSoup(resp.text, "html.parser")


def _parse_quote_block(block: BeautifulSoup) -> Quote:
    """Extract a Quote from a .quote div."""
    text_el = block.select_one("span.text")
    author_el = block.select_one("small.author")
    tag_els = block.select("div.tags a.tag")

    text = (text_el.get_text(strip=True) if text_el else "").strip("“”\"'")
    author = author_el.get_text(strip=True) if author_el else ""
    tags = [t.get_text(strip=True) for t in tag_els] if tag_els else []

    return Quote(text=text, author=author, tags=tags)


def scrape_all_quotes(base_url: str = BASE_URL) -> List[Quote]:
    """Traverse pagination and collect all quotes."""
    session = _session()
    quotes: List[Quote] = []

    next_url = base_url
    visited = set()

    while next_url and next_url not in visited:
        visited.add(next_url)
        soup = _get_soup(next_url, session)

        # Collect quotes on this page
        for qdiv in soup.select("div.quote"):
            quotes.append(_parse_quote_block(qdiv))

        # Follow pagination
        next_link = soup.select_one("li.next > a[href]")
        next_url = urljoin(next_url, next_link["href"]) if next_link else None

    return quotes


def _write_quotes_csv(quotes: Iterable[Quote], output_csv_path: str) -> None:
    """Write quotes to CSV (text, author, tags)."""
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "author", "tags"])
        writer.writeheader()
        for quote in quotes:
            writer.writerow({
                "text": f"“{quote.text}”",
                "author": quote.author,
                "tags": list(quote.tags),
            })


def main(output_csv_path: str) -> None:
    quotes = scrape_all_quotes(BASE_URL)
    _write_quotes_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
