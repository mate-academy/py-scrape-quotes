from dataclasses import dataclass
from typing import Generator
import csv

import requests
from bs4 import BeautifulSoup, Tag
from tqdm import tqdm

URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def page_generator() -> Generator[BeautifulSoup, None, None]:
    page_number = 1
    with requests.Session() as session:
        while True:
            request_url = f"{URL}page/{page_number}/"
            response = session.get(url=request_url)

            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.content, "html.parser")

            if not soup.find("div", class_="quote"):
                print(f"\n[Info] Сторінка {page_number} порожня. Завершуємо.")
                break

            yield soup
            page_number += 1


def parse_single_quote(quote: Tag) -> Quote:
    text = quote.find("span", class_="text").get_text(strip=True)
    author = quote.find("small", class_="author").get_text(strip=True)
    tags_elements = quote.find_all("a", class_="tag")
    tags = [tag.get_text(strip=True) for tag in tags_elements]

    return Quote(text=text, author=author, tags=tags)


def parse_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = []
    for quote in page_soup.find_all("div", class_="quote"):
        quotes.append(parse_single_quote(quote))

    return quotes


def get_quotes() -> list[Quote]:
    quotes = []
    for page_soup in tqdm(page_generator()):
        parsed_quotes = parse_page(page_soup)
        quotes.extend(parsed_quotes)

    return quotes


def write_to_csv(quotes: list[Quote], output_path: str) -> None:
    fieldnames = ["text", "author", "tags"]

    with open(output_path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for quote in quotes:
            writer.writerow({
                "text": quote.text,
                "author": quote.author,
                "tags": quote.tags,
            })


def main(output_csv_path: str) -> None:
    quotes = get_quotes()

    write_to_csv(quotes, output_csv_path)

    if quotes:
        print("Successfully parsed quotes.")
    else:
        print("Warning: No quotes found.")


if __name__ == "__main__":
    main("quotes.csv")
