import asyncio
import logging
import sys
import time

import aiohttp
from bs4 import BeautifulSoup

from app.models import Author, Quote
from app.utils import (
    BASE_URL,
    get_author_url,
    get_next_page_url,
    parse_author_bio,
    parse_single_quote,
    write_authors_to_csv,
    write_quotes_to_csv,
)

MAX_CONCURRENT_REQUESTS = 3


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)


async def get_page_content(session: aiohttp.ClientSession, url: str) -> str:
    """Get HTML content of the page."""
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def process_single_page(
    session: aiohttp.ClientSession,
    url: str,
    page_number: int,
    semaphore: asyncio.Semaphore,
    author_cache: dict[str, Author],
) -> tuple[list[Quote], str | None, list[Author]]:
    """
    Process a single page and return quotes with next page URL and authors.
    """
    async with semaphore:
        logging.info(f"Parsing page #{page_number}")
        page_content = await get_page_content(session, url)
        page_soup = BeautifulSoup(page_content, "html.parser")

        quotes_divs = page_soup.select(".quote")
        quotes = []
        new_authors = []
        author_tasks = []

        for quote_div in quotes_divs:
            quote = parse_single_quote(quote_div)
            quotes.append(quote)

            if quote.author not in author_cache:
                author_url = get_author_url(quote_div)
                task = asyncio.create_task(
                    get_page_content(session, author_url)
                )
                author_tasks.append((quote.author, task))

        for author_name, task in author_tasks:
            author_content = await task
            author_soup = BeautifulSoup(author_content, "html.parser")
            author = parse_author_bio(author_soup)
            author_cache[author_name] = author
            new_authors.append(author)
            logging.info(f"Collected biography for {author_name}")

        next_url = get_next_page_url(page_soup)
        return quotes, next_url, new_authors


async def get_page_urls(
    session: aiohttp.ClientSession, semaphore: asyncio.Semaphore
) -> list[str]:
    """Get all page URLs concurrently."""
    urls = []

    async with semaphore:
        current_url = BASE_URL

        while current_url:
            content = await get_page_content(session, current_url)
            soup = BeautifulSoup(content, "html.parser")

            if current_url != BASE_URL:
                urls.append(current_url)

            next_link = soup.select_one("li.next a")
            if not next_link:
                break

            current_url = get_next_page_url(soup)

        return urls


async def get_all_quotes() -> tuple[list[Quote], list[Author]]:
    """
    Collect all quotes and author biographies from all pages asynchronously.
    """
    all_quotes = []
    all_authors = []
    author_cache = {}
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession() as session:
        first_page = await process_single_page(
            session, BASE_URL, 1, semaphore, author_cache
        )
        all_quotes.extend(first_page[0])
        all_authors.extend(first_page[2])

        page_urls = await get_page_urls(session, semaphore)

        if page_urls:
            tasks = [
                process_single_page(
                    session, url, i + 2, semaphore, author_cache
                )
                for i, url in enumerate(page_urls)
            ]
            results = await asyncio.gather(*tasks)

            for quotes, _, authors in results:
                all_quotes.extend(quotes)
                all_authors.extend(authors)

    logging.info(f"Total quotes collected: {len(all_quotes)}")
    logging.info(f"Total authors collected: {len(all_authors)}")
    return all_quotes, all_authors


async def async_main(quotes_path: str, authors_path: str) -> None:
    """Scrape all quotes and authors, save them to CSV files."""
    logging.info("Starting quotes scraping...")
    quotes, authors = await get_all_quotes()
    write_quotes_to_csv(quotes, quotes_path)
    write_authors_to_csv(authors, authors_path)
    logging.info("Scraping complete!")


def main(
    quotes_path: str = "quotes.csv", authors_path: str = "authors.csv"
) -> None:
    """Entry point for synchronous execution."""
    asyncio.run(async_main(quotes_path, authors_path))


if __name__ == "__main__":
    start_time = time.time()
    main()
    execution_time = time.time() - start_time
    logging.info(f"Total execution time: {execution_time:.2f} seconds")  # noqa
