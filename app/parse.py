from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import csv


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_page(page_content: str) -> list[Quote]:
    soup = BeautifulSoup(page_content, "html.parser")
    quotes = []
    for quote in soup.select(".quote"):
        quotes.append(Quote(
            text=quote.select_one(".text").text,
            author=quote.select_one(".author").text,
            tags=[tag.text for tag in quote.select(".tag")],
        ))
    return quotes


def get_num_pages() -> int:
    page_number = 1
    while True:
        page = requests.get(f"{BASE_URL}page/{page_number}/")
        soup = BeautifulSoup(page.content, "html.parser")
        if not soup.select_one(".next"):
            break
        page_number += 1
    return page_number


def get_all_quotes() -> list[Quote]:
    quotes = []
    num_pages = get_num_pages()
    for i in range(1, num_pages + 1):
        page = requests.get(f"{BASE_URL}page/{i}/")
        quotes.extend(parse_single_page(page.content))
    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(
            output_csv_path,
            mode="w",
            encoding="utf-8",
            newline=""
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["text", "author", "tags"]
        )
        writer.writeheader()

        for quote in quotes:
            writer.writerow({
                "text": quote.text,
                "author": quote.author,
                "tags": quote.tags,
            })


if __name__ == "__main__":
    main("quotes.csv")
