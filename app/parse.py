import csv
import time
import dataclasses
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclasses.dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[a.text.strip() for a in quote.select("a.tag")],
    )


def scrape_quotes() -> list[Quote]:
    all_quotes = []
    url = BASE_URL
    while url:
        response = requests.get(url)
        response.raise_for_status()
        time.sleep(0.3)
        soup = BeautifulSoup(response.text, "html.parser")
        for element in soup.select("div.quote"):
            all_quotes.append(parse_single_quote(element))
        next_link = soup.select_one("li.next a")
        url = urljoin(BASE_URL, next_link["href"]) if next_link else None
    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str = "result.csv") -> None:
    write_quotes_to_csv(scrape_quotes(), output_csv_path)


if __name__ == "__main__":
    main("result.csv")
