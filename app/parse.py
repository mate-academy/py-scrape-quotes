import asyncio
import csv
import os
from dataclasses import dataclass, fields
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    born_date: str
    born_location: str
    description: str


async def get_soup(client: httpx.AsyncClient, url: str) -> BeautifulSoup:
    response = await client.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


async def parse_author(client: httpx.AsyncClient, author_url: str) -> Author:
    soup = await get_soup(client, author_url)
    return Author(
        name=soup.select_one(
            "h3.author-title"
        ).get_text(strip=True),
        born_date=soup.select_one(
            "span.author-born-date"
        ).get_text(strip=True),
        born_location=soup.select_one(
            "span.author-born-location"
        ).get_text(strip=True),
        description=soup.select_one(
            "div.author-description"
        ).get_text(strip=True),
    )


def parse_page(soup: BeautifulSoup) -> list[tuple[Quote, str]]:
    results = []
    for quote_div in soup.select("div.quote"):
        text = quote_div.select_one("span.text").get_text(strip=True)
        author = quote_div.select_one("small.author").get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag in quote_div.select("a.tag")]
        author_href = quote_div.select_one("a[href*='/author/']")["href"]
        results.append((
            Quote(text=text, author=author, tags=tags), author_href
        ))
    return results


async def scrape_pages(client: httpx.AsyncClient) -> list[tuple[Quote, str]]:
    all_pairs: list[tuple[Quote, str]] = []
    next_url: str | None = BASE_URL

    while next_url:
        soup = await get_soup(client, next_url)
        all_pairs.extend(parse_page(soup))
        next_link = soup.select_one("li.next > a")
        next_url = urljoin(BASE_URL, next_link["href"]) if next_link else None

    return all_pairs


async def fetch_author(
        client: httpx.AsyncClient,
        name: str,
        href: str) -> tuple[str, Author]:
    return name, await parse_author(client, urljoin(BASE_URL, href))


async def scrape() -> tuple[list[Quote], dict[str, Author]]:
    limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)

    async with httpx.AsyncClient(
            base_url=BASE_URL,
            limits=limits,
            timeout=30,
            follow_redirects=True) as client:
        all_pairs = await scrape_pages(client)

        quotes: list[Quote] = []
        author_hrefs: dict[str, str] = {}
        for quote, author_href in all_pairs:
            quotes.append(quote)
            author_hrefs.setdefault(quote.author, author_href)

        results = await asyncio.gather(
            *[
                fetch_author(client, name, href)
                for name, href in author_hrefs.items()
            ]
        )
        authors: dict[str, Author] = dict(results)

    return quotes, authors


def write_quotes_csv(quotes: list[Quote], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([field.name for field in fields(Quote)])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def write_authors_csv(authors: dict[str, Author], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([field.name for field in fields(Author)])
        for author in authors.values():
            writer.writerow([
                author.name,
                author.born_date,
                author.born_location,
                author.description
            ])


def main(output_csv_path: str) -> None:
    quotes, authors = asyncio.run(scrape())

    write_quotes_csv(quotes, output_csv_path)

    base, _ = os.path.splitext(output_csv_path)
    write_authors_csv(authors, base + "_authors.csv")


if __name__ == "__main__":
    main("quotes.csv")
