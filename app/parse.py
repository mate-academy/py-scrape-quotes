import csv
from dataclasses import dataclass, fields, astuple
from typing import Generator, List
import requests

from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"


def call_page(url: str) -> BeautifulSoup:
    response = requests.get(url, timeout=5)

    if response.status_code != 200:
        return None

    page = BeautifulSoup(response.content, "html.parser")

    if not page.select(".quote"):
        return None
    return page


def page_generator() -> Generator[BeautifulSoup, None, None]:
    page = 1

    while True:
        url = f"{BASE_URL}page/{page}"
        soup = call_page(url)

        if soup is None:
            break
        yield soup
        page += 1


def parse_page(soup: BeautifulSoup) -> List[Quote]:
    quotes = []
    elements = soup.select(".quote")
    for element in elements:
        text = element.select_one(".text").text
        author = element.select_one(".author").text
        tags = [tag.text for tag in element.select(".tag")]
        quotes.append(Quote(text, author, tags))
    return quotes


def get_all_quotes() -> List[Quote]:
    quotes = []
    for page in page_generator():
        quotes.extend(parse_page(page))
    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([f.name for f in fields(Quote)])
        writer.writerows([astuple(q) for q in quotes])


if __name__ == "__main__":
    main("quotes.csv")
