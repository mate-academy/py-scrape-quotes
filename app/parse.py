import asyncio
import csv
import logging
import sys
from dataclasses import astuple, dataclass, fields
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"
MAX_CONCURRENT_REQUESTS = 3


@dataclass
class Author:
    name: str
    born_date: str
    born_location: str
    description: str


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)


def parse_single_quote(quote_div: Tag) -> Quote:
    return Quote(
        text=quote_div.select_one(".text").text,
        author=quote_div.select_one(".author").text,
        tags=[tag.text for tag in quote_div.select(".tag")],
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes_divs = page_soup.select(".quote")
    return [parse_single_quote(quote_div) for quote_div in quotes_divs]


def get_next_page_url(page_soup: Tag) -> str | None:
    next_button = page_soup.select_one("li.next a")

    if next_button:
        return urljoin(BASE_URL, next_button["href"])

    return None


def get_author_url(quote_div: Tag) -> str:
    about_link = quote_div.select_one(".author + a")
    return urljoin(BASE_URL, about_link["href"])


async def get_page_content(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


def parse_author_bio(page_soup: Tag) -> Author:
    born_date = page_soup.select_one(".author-born-date").text
    born_location = page_soup.select_one(".author-born-location").text
    description = page_soup.select_one(".author-description").text.strip()
    name = page_soup.select_one(".author-title").text

    return Author(name, born_date, born_location, description)


async def process_single_page(
    session: aiohttp.ClientSession,
    url: str,
    page_number: int,
    semaphore: asyncio.Semaphore,
    author_cache: dict[str, Author],
) -> tuple[list[Quote], str | None, list[Author]]:

    async with semaphore:
        logging.info(f"Parsing page #{page_number}")
        page_content = await get_page_content(session, url)
        page_soup = BeautifulSoup(page_content, "html.parser")

        quotes_divs = page_soup.select(".quote")
        quotes = []
        new_authors = []

        for quote_div in quotes_divs:
            quote = parse_single_quote(quote_div)
            quotes.append(quote)

            if quote.author not in author_cache:
                author_url = get_author_url(quote_div)
                author_content = await get_page_content(session, author_url)
                author_soup = BeautifulSoup(author_content, "html.parser")
                author = parse_author_bio(author_soup)
                author_cache[quote.author] = author
                new_authors.append(author)
                logging.info(f"Collected biography for {quote.author}")

        next_url = get_next_page_url(page_soup)
        return quotes, next_url, new_authors


async def get_all_quotes() -> tuple[list[Quote], list[Author]]:
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
        next_url = first_page[1]

        page_urls = []
        page_number = 2
        current_url = next_url

        while current_url:
            page_urls.append(current_url)
            page_content = await get_page_content(session, current_url)
            page_soup = BeautifulSoup(page_content, "html.parser")
            current_url = get_next_page_url(page_soup)
            page_number += 1

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


def write_quotes_to_csv(quotes: list[Quote], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])

    logging.info(f"Quotes have been saved to {output_path}")


def write_authors_to_csv(authors: list[Author], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(AUTHOR_FIELDS)
        writer.writerows([astuple(author) for author in authors])

    logging.info(f"Authors have been saved to {output_path}")


async def async_main(quotes_path: str, authors_path: str) -> None:
    logging.info("Starting quotes scraping...")
    quotes, authors = await get_all_quotes()
    write_quotes_to_csv(quotes, quotes_path)
    write_authors_to_csv(authors, authors_path)
    logging.info("Scraping complete!")


def main(
    quotes_path: str = "quotes.csv", authors_path: str = "authors.csv"
) -> None:
    asyncio.run(async_main(quotes_path, authors_path))


if __name__ == "__main__":
    main()
