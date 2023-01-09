import csv
import time
import asyncio
from urllib.parse import urljoin
from dataclasses import dataclass, astuple, fields

import httpx
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Author:
    name: str
    url: str
    biography: str | None


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


async def get_all_quotes(output_csv_path: str) -> None:
    with open(output_csv_path, mode="w", encoding="utf-8", newline="") as output_csv:
        object_writer = csv.writer(output_csv)
        object_writer.writerow([field.name for field in fields(Quote)])
        coroutines = [
            parse_single_page(urljoin(BASE_URL, f"page/{page}/"), object_writer)
            for page in range(1, 11)
        ]
        await asyncio.gather(*coroutines)


async def parse_single_page(url: str, object_writer) -> None:
    async with httpx.AsyncClient() as client:
        page = await client.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    quotes = soup.select(".quote")
    for quote in quotes:
        object_writer.writerow(astuple(parse_single_quote(quote)))


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        quote.select_one(".text").text,
        quote.select_one(".author").text,
        [tag.text for tag in quote.select(".tag")]
    )


async def main(output_csv_path: str) -> None:
    await get_all_quotes(output_csv_path)

if __name__ == "__main__":
    start = time.perf_counter()
    asyncio.run(main("quotes.csv"))
    end = time.perf_counter()
    print("Elapsed:", end - start)
