import asyncio
import csv
from dataclasses import dataclass
from typing import Any, AsyncGenerator
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm_asyncio

URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class AuthorBio:
    name: str
    born_date: str
    born_location: str
    description: str


async def fetch_page_content(
    client: httpx.AsyncClient,
    url: str
) -> bytes | None:
    try:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content
    except httpx.RequestError as e:
        print(f"Request failed for {url}: {e}")
        return None


async def page_generator(
    client: httpx.AsyncClient,
    base_url: str
) -> AsyncGenerator[BeautifulSoup, Any]:
    page_counter = 1
    while True:
        page_url = urljoin(base_url, f"page/{page_counter}/")
        content = await fetch_page_content(client, page_url)
        if not content:
            break
        soup = BeautifulSoup(content, "lxml")
        if not soup.select(".quote"):
            break
        yield soup
        page_counter += 1


def parse_page(page: BeautifulSoup) -> list[Quote]:
    quotes = []
    for quote_html in page.select(".quote"):
        author = quote_html.select_one(".author").text.strip()
        text = quote_html.select_one(".text").text.strip()
        tags = [tag.text for tag in quote_html.select(".tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))
    return quotes


def parse_page_with_author_links(
    page: BeautifulSoup
) -> list[tuple[Quote, str]]:
    quotes = []
    for quote_html in page.select(".quote"):
        author = quote_html.select_one(".author").text.strip()
        text = quote_html.select_one(".text").text.strip()
        tags = [tag.text for tag in quote_html.select(".tag")]
        author_link = quote_html.select_one(".author + a")
        author_url = urljoin(URL, author_link["href"]) if author_link else None
        quotes.append((Quote(text=text, author=author, tags=tags), author_url))
    return quotes


async def fetch_author_bio(
    client: httpx.AsyncClient, author_url: str
) -> AuthorBio | None:
    if not author_url.endswith("/"):
        author_url += "/"

    content = await fetch_page_content(client, author_url)
    if not content:
        return None
    soup = BeautifulSoup(content, "lxml")
    name = soup.select_one(".author-title").text.strip()
    born_date = soup.select_one(".author-born-date").text.strip()
    born_location = soup.select_one(".author-born-location").text.strip()
    description = soup.select_one(".author-description").text.strip()
    return AuthorBio(
        name=name,
        born_date=born_date,
        born_location=born_location,
        description=description,
    )


async def get_all_quotes_and_authors(
) -> tuple[list[Quote], dict[str, AuthorBio]]:  # noqa: E501
    all_quotes = []
    author_urls = {}
    async with httpx.AsyncClient() as client:
        async for page in page_generator(client, URL):
            for quote, author_url in parse_page_with_author_links(page):
                all_quotes.append(quote)
                if author_url and quote.author not in author_urls:
                    author_urls[quote.author] = author_url
        bios = await tqdm_asyncio.gather(
            *(fetch_author_bio(client, url) for url in author_urls.values()),
            desc="Fetching author bios",
        )
        author_bios = {
            author: bio for author, bio in zip(author_urls.keys(), bios) if bio
        }
    return all_quotes, author_bios


def export_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            tags_str = str(quote.tags).replace('"', "'")
            writer.writerow([quote.text, quote.author, tags_str])


def export_authors_to_csv(
    authors: dict[str, AuthorBio], output_csv_path: str
) -> None:

    with open(output_csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["name", "born_date", "born_location", "description"])
        for bio in authors.values():
            writer.writerow(
                [bio.name, bio.born_date, bio.born_location, bio.description]
            )


async def main(output_csv_path: str, authors_csv_path: str = None) -> None:
    quotes, authors = await get_all_quotes_and_authors()
    export_to_csv(quotes, output_csv_path)
    if authors_csv_path:
        export_authors_to_csv(authors, authors_csv_path)


if __name__ == "__main__":
    asyncio.run(main("quotes.csv", "authors.csv"))
