import csv
import requests

from dataclasses import dataclass
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from app.parse_author_bios import write_bio_to_csv

load_dotenv()


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]
    author_page_url: str = None


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    anchor_tag = quote_soup.select_one(".author + a")

    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
        author_page_url=anchor_tag.get("href"),
    )


def get_single_page_quotes(quote_soup: BeautifulSoup) -> list[Quote]:
    quotes = quote_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes(base_url: str) -> list[Quote]:
    page = requests.get(base_url).content
    first_page_soup = BeautifulSoup(page, "html.parser")
    all_quotes = get_single_page_quotes(first_page_soup)

    i = 2
    while True:
        next_page = urljoin(base_url, f"/page/{i}")
        next_page_url = requests.get(next_page).content
        next_page_soup = BeautifulSoup(next_page_url, "html.parser")

        quotes_on_page = get_single_page_quotes(next_page_soup)

        if not quotes_on_page:
            break

        all_quotes.extend(quotes_on_page)
        i += 1

    return all_quotes


def main(output_csv_path: str) -> None:
    # base_url = os.environ.get("BASE_URL")
    base_url = "https://quotes.toscrape.com/"

    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["text", "author", "tags"])
        quotes = get_quotes(base_url)

        for quote in quotes:
            text = quote.text
            author = quote.author
            tags = quote.tags
            writer.writerow([text, author, tags])


if __name__ == "__main__":
    write_bio_to_csv("bios.csv")
    main("quotes.csv")
