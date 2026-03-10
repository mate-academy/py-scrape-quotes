import csv

from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

import requests


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: str


def parse_single_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").get_text(strip=True)

    tags = str(
        [
            tag.get_text(strip=True)
            for tag in quote.select(".tags a.tag")
        ]
    )

    return Quote(
        text=text,
        author=quote.select_one(".author").text,
        tags=tags
    )


def get_next_page(soup: BeautifulSoup) -> str | None:
    next_btn = soup.select_one(".next a")

    if next_btn:
        return BASE_URL + next_btn["href"]

    return None


def get_all_quotes() -> list[Quote]:
    url = BASE_URL
    quotes = []

    while url:
        response = requests.get(url)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")

        quotes.extend(
            parse_single_quote(q) for q in soup.select(".quote")
        )
        url = get_next_page(soup)

    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([
                quote.text,
                quote.author,
                quote.tags
            ])


if __name__ == "__main__":
    main("quotes.csv")
