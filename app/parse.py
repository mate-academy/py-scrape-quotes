import asyncio
import csv
import time
from dataclasses import dataclass
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup, SoupStrainer

BASE_URL = "https://quotes.toscrape.com/"
NEXT_PAGE_URL = "page/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()


def parse_single_quote(quote_element: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_element.select_one(".text").text,
        author=quote_element.select_one(".author").text,
        tags=[tag.text for tag in quote_element.select(".tag")],
    )


def filter_for_quotes_elements(tag: str, tag_args: dict) -> bool:
    return tag == "div" and "quote" == tag_args.get("class")


quotes_strainer = SoupStrainer(filter_for_quotes_elements)
pagination_strainer = SoupStrainer("ul", class_="pager")


async def get_all_page_quotes(
    session: aiohttp.ClientSession, page_url: str
) -> list[Quote]:
    page = await fetch_url(session, page_url)
    soup = BeautifulSoup(page, "html.parser", parse_only=quotes_strainer)
    quotes_elements = soup.select(".quote")
    quotes_instances = [parse_single_quote(quote) for quote in quotes_elements]
    return quotes_instances


async def get_all_quotes_instances_async(
    base_url: str = BASE_URL,
) -> list[Quote]:
    page_count = 1
    quotes_list = []
    async with aiohttp.ClientSession() as session:
        while True:
            page_link = urljoin(base_url, f"{NEXT_PAGE_URL}{page_count}/")
            current_page_quotes = await get_all_page_quotes(session, page_link)
            quotes_list.extend(current_page_quotes)

            page_count += 1
            if not current_page_quotes:
                break
    return quotes_list


def write_quotes_to_csv(
    quotes_list: list[Quote], output_csv_path: str
) -> None:
    with open(output_csv_path, "w", newline="") as csv_file:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for quote in quotes_list:
            writer.writerow(
                {
                    "text": quote.text,
                    "author": quote.author,
                    "tags": ", ".join(quote.tags),
                }
            )


async def main(output_csv_path: str) -> None:
    quotes_list = await get_all_quotes_instances_async()
    write_quotes_to_csv(quotes_list, output_csv_path)


if __name__ == "__main__":
    print(time.strftime("%X"))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main("quotes.csv"))
    print(time.strftime("%X"))
