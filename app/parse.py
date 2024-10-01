import csv
from dataclasses import dataclass, asdict
from typing import List, Coroutine

from bs4 import BeautifulSoup, Tag
from httpx import AsyncClient
import asyncio


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    def dict(self) -> dict:
        return {k: str(v) for k, v in asdict(self).items()}


async def get_soup(
    client: AsyncClient,
    page: str
) -> BeautifulSoup:
    response = await client.get(url=page)
    page = response.text
    soup = BeautifulSoup(markup=page, features="html.parser")
    return soup


def get_tags(page_tag: Tag) -> List[str]:
    return [tag.text for tag in page_tag.select(".tag")]


def map_quote(page_tag: Tag) -> Quote:
    quote = Quote(
        text=page_tag.select_one(".text").text,
        author=page_tag.select_one(".author").text,
        tags=get_tags(page_tag)
    )
    return quote


def parce_single_page(soup: BeautifulSoup) -> List[Quote]:
    page_tags = soup.select(".quote")
    quotes = [
        map_quote(page_tag)
        for page_tag
        in page_tags
    ]

    return quotes


def get_tasks(client: AsyncClient) -> List[Coroutine]:
    urls = [BASE_URL]
    urls.extend([
        BASE_URL + f"/page/{n}/"
        for n in range(2, 11)
    ])
    tasks = [
        get_soup(client=client, page=url)
        for url in urls
    ]
    return tasks


async def get_all_quotes() -> List[Quote]:
    async with AsyncClient() as client:
        soups = await asyncio.gather(*get_tasks(client))
    quotes = []
    for soup in soups:
        quotes.extend(parce_single_page(soup))
    return quotes


def main(output_csv_path: str) -> None:
    quotes = asyncio.run(get_all_quotes())
    with open(
            file=output_csv_path,
            mode="w",
            newline="") as csvfile:
        fieldnames = quotes[0].dict().keys()

        quotewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        quotewriter.writeheader()

        for quote in quotes:
            quotewriter.writerow(quote.dict())


if __name__ == "__main__":
    main("quotes.csv")
