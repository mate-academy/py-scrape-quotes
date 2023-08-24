import asyncio


import httpx
from bs4 import BeautifulSoup

from app.utils import get_quotes_on_page, write_quotes_to_file_async

BASE_URL = "https://quotes.toscrape.com"


async def main(output_csv_path: str) -> None:
    page_number = 1
    stop_event = asyncio.Event()

    while not stop_event.is_set():
        tasks = [get_page(page_number, output_csv_path, stop_event)]
        page_number += 1

        await asyncio.gather(*tasks)


async def get_page(
        page_number: int,
        output_file: str,
        stop_event: asyncio.Event
) -> None:
    url = f"{BASE_URL}/page/{page_number}/"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    page_content = response.content
    soup = BeautifulSoup(page_content, "html.parser")
    quotes_soup = soup.select(".quote")

    if not quotes_soup:
        stop_event.set()
        return

    quotes = get_quotes_on_page(quotes_soup)

    await write_quotes_to_file_async(
        quotes_instances=quotes,
        output_file=output_file
    )


if __name__ == "__main__":
    asyncio.run(main("quotes.csv"))
