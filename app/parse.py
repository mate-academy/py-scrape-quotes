import csv
from dataclasses import dataclass, astuple
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import Generator
from tqdm import tqdm
import requests


URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_page(page: BeautifulSoup) -> list[Quote]:
    result = []
    quotes = page.select(".quote")

    for quote in quotes:
        author = quote.select_one(".author").text.strip()
        text = quote.select_one(".text").text.strip()
        tags = [tag.text for tag in quote.select(".tag")]
        result.append(Quote(text=text, author=author, tags=tags))
    return result


def get_quotes() -> list[Quote]:
    result = []
    for page in tqdm(page_generator(URL)):
        result.extend(parse_page(page))
    return result


def page_generator(url: str) -> Generator[BeautifulSoup, None, None]:
    """
    Generate a BeautifulSoup object from page content for each page
    """
    page_counter = 0
    while True:
        page_counter += 1
        page_url = urljoin(url, f"page/{page_counter}/")
        if content := fetch_page_content(page_url):
            yield BeautifulSoup(content, "lxml")
        elif not content:
            break
        soup = BeautifulSoup(content, "lxml")
        if not soup.select(".quote"):
            break


def export_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["author", "text", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


def fetch_page_content(url: str) -> bytes | None:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(e)


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    export_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
