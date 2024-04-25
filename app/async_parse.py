import csv
from dataclasses import dataclass

import asyncio
import aiohttp
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/page/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


all_quotes = []


def parse_single_quote(soup: BeautifulSoup) -> Quote:
    return Quote(
        text=soup.select_one(".text").text.strip(),
        author=soup.select_one(".author").text.strip(),
        tags=[tag.text.strip() for tag in soup.select(".tags > a.tag")],
    )


async def pages_counter() -> int:
    page_counter = 1
    next_page = True
    async with aiohttp.ClientSession() as session:
        while next_page:
            url = BASE_URL + f"{page_counter}/"
            async with session.get(url, ssl=False) as response:
                page_content = await response.content.read()
                soup = BeautifulSoup(page_content, "html.parser")
                next_page = soup.select_one(".next")
                page_counter += 1
    return page_counter


async def get_page_data(session: aiohttp.ClientSession, page: int) -> None:
    url = BASE_URL + f"{page}/"
    async with session.get(url, ssl=False) as response:
        response = await response.content.read()
        soup = BeautifulSoup(response, "html.parser")
        quotes = soup.select(".quote")
        for quote in quotes:
            all_quotes.append(parse_single_quote(quote))
        print(f"INFO: page {page} finished")


async def gather_data() -> None:
    async with aiohttp.ClientSession() as session:
        tasks = []
        last_page_number = await pages_counter()
        for page in range(1, last_page_number):
            tasks.append(asyncio.create_task(get_page_data(session, page)))
        await asyncio.gather(*tasks)


async def main(output_csv_path: str) -> None:
    await gather_data()
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in all_quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    asyncio.run(main("result.csv"))
