import csv
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text.strip(),
        author=quote.select_one(".author").text.strip(),
        tags=[tag.text.strip() for tag in quote.select(".tag")],
    )


def get_all_quotes() -> list[Quote]:
    quotes = []
    next_page = "/page/1/"
    while next_page:
        url = urljoin(BASE_URL, next_page)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        for quote_block in soup.select(".quote"):
            quotes.append(parse_single_quote(quote_block))

        next_btn = soup.select_one(".next > a")
        next_page = next_btn["href"] if next_btn else None

    return quotes


def save_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            tags_str = ", ".join(quote.tags)
            writer.writerow([quote.text, quote.author, tags_str])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    save_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
