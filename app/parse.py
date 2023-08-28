import csv
from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests


URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_page(soup: BeautifulSoup) -> list[Quote] | int:
    quotes_items = soup.select(".quote")

    if not quotes_items:
        return -1

    quotes = []
    for quote_item in quotes_items:
        quotes.append(
            Quote(
                text=quote_item.select_one(".text").text,
                author=quote_item.select_one(".author").text,
                tags=[tag.text for tag in quote_item.select(".tag")]
            )
        )

    return quotes


def get_parsed_data() -> list[Quote]:
    response = requests.get(URL).content
    first_page = BeautifulSoup(response, features="html.parser")

    parsed = []
    parsed.extend(parse_single_page(first_page))

    page = 2
    while True:
        response = requests.get(urljoin(URL, f"page/{page}")).content
        current_page = BeautifulSoup(response, features="html.parser")

        res = parse_single_page(current_page)
        if res == -1:
            break

        parsed.extend(res)

        page += 1
    return parsed


def main(output_csv_path: str) -> None:
    data = get_parsed_data()
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in data:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
