import asyncio
import csv
import json
from dataclasses import dataclass, fields

import aiohttp
from bs4 import BeautifulSoup, Tag
from tqdm.asyncio import tqdm

URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]
    author_bio: str


QUOTE_FIELDS = [field.name for field in fields(Quote)]

BIO_CACHE = {}


async def fetch_author_bio(session: aiohttp.ClientSession, url: str) -> str:
    if url in BIO_CACHE:
        return BIO_CACHE[url]

    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, "lxml")
        desc_element = soup.select_one(".author-description")
        bio = desc_element.text.strip() if desc_element else "Bio not found"

        BIO_CACHE[url] = bio
        return bio


async def parse_single_quote(
        session: aiohttp.ClientSession,
        quote: Tag
) -> Quote:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags = [t.text for t in quote.select(".tag")]
    author_partial_link = quote.select_one("span a")["href"]
    full_author_url = URL.rstrip("/") + author_partial_link
    bio = await fetch_author_bio(session, full_author_url)

    return Quote(
        text=text,
        author=author,
        tags=tags,
        author_bio=bio,
    )


async def parse_page(
        session: aiohttp.ClientSession,
        page_number: int
) -> list[Quote] | None:
    request_url = f"{URL}/page/{page_number}/"
    async with session.get(request_url) as response:
        if response.status != 200:
            return None

        html = await response.text()
        soup = BeautifulSoup(html, "lxml")
        quote_tags = soup.select(".quote")

        if not quote_tags:
            return None

        tasks = [parse_single_quote(session, q) for q in quote_tags]
        quotes = await asyncio.gather(*tasks)

        return quotes


async def get_quotes() -> list[Quote]:
    quotes = []
    page_number = 1
    async with aiohttp.ClientSession() as session:
        with tqdm(desc="Scraping pages") as pbar:
            while True:
                page_quotes = await parse_page(session, page_number)
                if page_quotes is None:
                    break

                quotes.extend(page_quotes)
                page_number += 1
                pbar.update(1)

    return quotes


def write_quotes_to_csv(quotes: list[Quote], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)
        for quote in quotes:
            writer.writerow([
                quote.text,
                quote.author,
                json.dumps(quote.tags),
                quote.author_bio,
            ])


async def async_main(output_csv_path: str) -> None:
    quotes = await get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


def main(output_csv_path: str) -> None:
    asyncio.run(async_main(output_csv_path))


if __name__ == "__main__":
    main("quotes.csv")
