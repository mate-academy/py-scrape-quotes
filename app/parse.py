import csv
from dataclasses import dataclass, asdict
from typing import Generator

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def page_generator() -> Generator[BeautifulSoup, None, None]:
    page_number = 1
    with requests.Session() as session:
        while True:
            request_url = f"{BASE_URL}/page/{page_number}/"
            response = session.get(url=request_url)
            if response.status_code != 200:
                print("The end, folks!")
                break
            soup = BeautifulSoup(response.content, "html.parser")
            if not soup.select(".quote"):
                print(f"No quotes found on page {page_number}. Stopping.")
                break
            yield soup
            page_number += 1


def parse_single_quote(quote: Tag) -> Quote:
    text = quote.select_one("span.text").get_text(strip=True)
    author = quote.select_one("small.author").get_text(strip=True)
    tags_block = quote.select_one("div.tags")
    tags_elements = tags_block.select("a.tag")
    tags = [tag.get_text(strip=True) for tag in tags_elements]
    return Quote(
        text=text,
        author=author,
        tags=tags
    )


def parse_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = []
    for quote in page_soup.select(".quote"):
        quotes.append(parse_single_quote(quote))
    return quotes


def get_quotes() -> list[Quote]:
    quotes = []
    for page_soup in tqdm(page_generator()):
        parsed_books = parse_page(page_soup)
        quotes.extend(parsed_books)
    return quotes


def save_to_csv(quotes: list[Quote], output_path: str) -> None:
    if not quotes:
        return

    with open(output_path, mode="w", encoding="utf-8", newline="") as file:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for quote in quotes:
            data = asdict(quote)

            writer.writerow(data)


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    save_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
