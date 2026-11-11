import csv
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"
START_URL = urljoin(BASE_URL, "page/1/")


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:
    keywords_content = quote.select_one(".keywords")["content"]

    tags_list = keywords_content.split(",") if keywords_content else []

    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=tags_list,
    )


def get_single_page_quotes(page_soup: Tag) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_page_quotes() -> [Quote]:
    current_url = START_URL
    all_quotes = []

    while current_url:
        text = requests.get(current_url).content
        page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(page_soup))

        next_page = page_soup.select_one("li.next a")
        current_url = urljoin(
            BASE_URL,
            next_page["href"]
        ) if next_page else None

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_page_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
