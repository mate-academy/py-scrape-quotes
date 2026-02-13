from dataclasses import dataclass
from typing import Generator
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag
import csv
from tqdm import tqdm


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
            url = urljoin(BASE_URL, f"page/{page_number}/")
            response = session.get(url)

            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.content, "html.parser")

            if not soup.select(".quote"):
                break

            yield soup
            page_number += 1


def parse_single_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").get_text(strip=True)
    author = quote.select_one(".author").get_text(strip=True)
    tags = [tag.get_text(strip=True) for tag in quote.select(".tag")]

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
        parsed_quotes = parse_page(page_soup)
        quotes.extend(parsed_quotes)
    return quotes


def write_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([
                quote.text,
                quote.author,
                ", ".join(quote.tags)
            ])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
