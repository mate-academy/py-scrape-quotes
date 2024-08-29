import csv
from dataclasses import dataclass, fields, astuple
from typing import Generator
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag
from tqdm import tqdm

URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    def __str__(self) -> str:
        return (
            f"Author: {self.author}\n"
            f"Tags: {self.tags}\n"
            f"{self.text}\n"
        )


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def fetch_page_content(url: str) -> bytes | None:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Content does not exist: {e}")


def page_generator(url: str) -> Generator[BeautifulSoup, None, None]:
    page_counter = 1
    while True:
        page_url = urljoin(url, f"page/{page_counter}/")
        page_content = fetch_page_content(page_url)
        if page_content:
            yield BeautifulSoup(page_content, "html.parser")
        if not BeautifulSoup(page_content, "html.parser").find(class_="next"):
            break
        page_counter += 1


def parse_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags_list = quote.select(".tag")
    tags = [tag.text for tag in tags_list]
    return Quote(text=text, author=author, tags=tags)


def extract_quotes(soup: BeautifulSoup) -> list[Quote]:
    quotes = soup.select(".quote")
    return [parse_quote(quote) for quote in quotes]


def scrape_quotes() -> list[Quote]:
    quotes = []
    for page in tqdm(page_generator(URL)):
        quotes.extend(extract_quotes(page))
    return quotes


def write_quotes_to_csv(quotes: [Quote], filename: str) -> None:
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
