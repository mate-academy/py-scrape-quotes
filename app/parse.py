import asyncio
import csv
from dataclasses import dataclass
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    def __str__(self) -> str:
        return f"{self.text} | {self.author} | {self.tags}"


def parse_tag(soup: BeautifulSoup) -> list[str]:
    return [i.get_text() for i in soup.find_all("a", "tag")]


def create_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.find("span", "text").text
    author = quote_soup.find("small", "author").text
    tags = parse_tag(quote_soup.find("div", "tags"))

    return Quote(
        text=text,
        author=author,
        tags=tags
    )


async def get_quotes(session: Any, url: str) -> list[Quote]:
    async with session.get(url) as resp:
        data = await resp.text()
        soup = BeautifulSoup(data, "html.parser")

        quotes = soup.find_all(
            "div", class_="quote"
        )

        return [create_quote(quote) for quote in quotes]


async def parse_site() -> Any:
    async with aiohttp.ClientSession() as session:
        quotes = []
        for page in range(1, 11):
            url = f"{URL}/page/{page}"
            quotes.append(asyncio.ensure_future(get_quotes(session, url)))

        ready_data = await asyncio.gather(*quotes)

        return ready_data


def main(output_csv_path: str) -> None:
    data = asyncio.run(parse_site())

    with open(output_csv_path, "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["text", "author", "tags"])
        for page in data:
            for quote in page:
                csvwriter.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
