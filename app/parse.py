import csv
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup

URL = "https://quotes.toscrape.com/"


def get_page(url: str) -> BeautifulSoup:
    response = requests.get(url=url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


@dataclass
class Quote:
    text: str
    author: str
    tags: str


def get_quotes(soup: BeautifulSoup) -> List[Quote]:
    queue_list = []
    for quote in soup.select(".quote"):
        text = quote.select_one(".text").get_text(strip=True)
        author = quote.select_one(".author").get_text(strip=True)

        tags_list = [tag.get_text(strip=True) for tag in quote.select(".tag")]
        tags = str(tags_list)

        queue_list.append(Quote(text=text, author=author, tags=tags))

    return queue_list


def get_all_quotes() -> List[Quote]:
    quotes = []
    url = URL

    while url:
        soup = get_page(url)

        quotes.extend(get_quotes(soup))

        next_btn = soup.select_one(".next a")
        url = URL + next_btn["href"] if next_btn else None

    return quotes


def save_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    save_to_csv(quotes, output_csv_path)
    print(f"{len(quotes)} quotes saved to {output_csv_path}")


if __name__ == "__main__":
    main("quotes.csv")
