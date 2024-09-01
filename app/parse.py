import csv
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin

import aiohttp
import asyncio
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


async def fetch_page_content(
        session: aiohttp.ClientSession, page_url: str
) -> Optional[bytes]:
    try:
        async with session.get(page_url) as response:
            response.raise_for_status()
            return await response.read()
    except aiohttp.ClientError as error:
        print("Error fetching page", error)
        return None


async def get_quotes_from_page(
        session: aiohttp.ClientSession, page_num: int
) -> List[Quote]:
    page_url = urljoin(BASE_URL, f"/page/{page_num}/")
    page_content = await fetch_page_content(session, page_url)

    if not page_content:
        return []

    soup = BeautifulSoup(page_content.decode("utf-8"), "html.parser")
    quote_elements = soup.select(".quote")
    quotes = []

    if quote_elements:
        for element in quote_elements:
            text = element.select_one(".text").get_text()
            author = element.select_one(".author").get_text()
            tags = [
                tag.get_text()
                for tag in element.select(".tag")
            ]
            quotes.append(Quote(text=text, author=author, tags=tags))
        print(f"Successfully scrapped page №{page_num}")
    return quotes


async def get_quotes(pages_amount: int) -> List[Quote]:
    async with aiohttp.ClientSession() as session:
        quotes = []
        page_num = 1
        while True:
            tasks = [
                get_quotes_from_page(session, page)
                for page in range(page_num, page_num + pages_amount)
            ]
            results = await asyncio.gather(*tasks)

            if not any(results):
                break

            for quote in results:
                quotes.extend(quote)

            page_num += pages_amount

        return quotes


async def write_quotes_to_csv(
        quotes: List[Quote], output_csv_path: str
) -> None:
    with open(
            output_csv_path, mode="w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow(
                [quote.text, quote.author, quote.tags]
            )


def main(output_csv_path: str) -> None:
    pages_to_scrap_in_parallel = 10
    quotes = asyncio.run(get_quotes(pages_to_scrap_in_parallel))
    asyncio.run(write_quotes_to_csv(quotes, output_csv_path))


if __name__ == "__main__":
    main("quotes.csv")
