import asyncio
import csv
from dataclasses import dataclass, fields, astuple
from typing import List
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


async def parse_single_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tags > .tag")]
    )


async def get_single_page(page: BeautifulSoup) -> List[Quote]:
    quotes = page.select(".quote")
    return [await parse_single_quote(quote) for quote in quotes]


async def get_quotes() -> List[Quote]:
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL)
        base_page = response.content
        first_page = BeautifulSoup(base_page, "html.parser")
        all_pages = await get_single_page(first_page)
        next_page = first_page.select_one(".next > a")

        while next_page:
            new_url = urljoin(BASE_URL, next_page["href"])
            response = await client.get(new_url)
            page_content = response.content
            parsed_page = BeautifulSoup(page_content, "html.parser")
            all_pages.extend(await get_single_page(parsed_page))
            next_page = parsed_page.select_one(".next > a")

    return all_pages


async def write_products_to_csv(path: str, quotes: list[Quote]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


async def retrieve_quotes(output_csv_path: str) -> None:
    quotes = await get_quotes()
    await write_products_to_csv(output_csv_path, quotes)


def main(output_csv_path: str) -> None:
    asyncio.run(retrieve_quotes(output_csv_path))


if __name__ == "__main__":
    main("quotes.csv")
