import csv
from dataclasses import dataclass
import requests

from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"
QUOTES = ["text", "author", "tags"]


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_page(url: str) -> BeautifulSoup:
    response = requests.get(url)
    return BeautifulSoup(response.content, "html.parser")


def get_num_page(page_soup: BeautifulSoup) -> int:
    next_page = page_soup.select_one(".next")
    if next_page:
        return int(next_page["href"].split("/")[-2])


def scrape_quotes(page_soup: BeautifulSoup) -> list:
    quotes = []
    for elem in page_soup.select(".quote"):
        text = elem.select_one(".text").text
        author = elem.select_one(".author").text
        tags = [tag.text for tag in elem.select(".tag")]
        quotes.append(Quote(text, author, tags))
    return quotes


def main(output_csv_path: str) -> None:
    page_num = 1

    with open(output_csv_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=QUOTES)
        writer.writeheader()

        while True:
            page_url = f"{BASE_URL}page/{page_num}"
            page_soup = get_page(page_url)
            quotes = scrape_quotes(page_soup)

            if not quotes:
                break

            for quote in quotes:
                writer.writerow({
                    "text": quote.text,
                    "author": quote.author,
                    "tags": quote.tags
                })
            page_num += 1


if __name__ == "__main__":
    main("quotes.csv")
