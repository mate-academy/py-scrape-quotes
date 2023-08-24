import csv
from typing import List

import aiofiles
from aiocsv import AsyncDictWriter
from bs4.element import Tag

from app.entities import Quote


def get_quotes_on_page(quotes_soup: List[Tag]) -> List[Quote]:
    return [get_single_quote(quote_soup) for quote_soup in quotes_soup]


def get_single_quote(quote_soup: Tag) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one("small.author").text
    tags = [tag.text for tag in quote_soup.select(".tags > .tag")]

    return Quote(text=text, author=author, tags=tags)


async def write_quotes_to_file_async(
        quotes_instances: List[Quote],
        output_file: str
) -> None:
    async with aiofiles.open(
            output_file,
            mode="a+",
            encoding="utf-8",
            newline=""
    ) as quotes_file:
        file_exists = await quotes_file.tell() != 0
        writer = AsyncDictWriter(
            quotes_file,
            ["text", "author", "tags"],
            restval="NULL",
            quoting=csv.QUOTE_ALL
        )

        if not file_exists:
            await writer.writeheader()

        for quote in quotes_instances:
            await writer.writerow(quote.__dict__)
