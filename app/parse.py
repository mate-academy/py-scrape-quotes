import csv
from dataclasses import dataclass, asdict
from typing import List

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_single_quotes(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [get_single_quotes(quote_soup) for quote_soup in quotes]


def parse_quotes(url: str) -> list[Quote]:
    all_quotes = []
    while url:
        print(f"Scraping {url}")
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        next_page = soup.select_one(".next > a")
        url = BASE_URL + next_page["href"] if next_page else None
    return all_quotes


def create_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for quote in quotes:
            quote_dict = asdict(quote)
            quote_dict["tags"] = str(quote_dict["tags"])
            writer.writerow(quote_dict)


def main(output_csv_path: str) -> None:
    quotes = parse_quotes(BASE_URL)
    create_csv(quotes, output_csv_path)
    print(f"Quotes successfully written to {output_csv_path}")


if __name__ == "__main__":
    main("quotes.csv")
