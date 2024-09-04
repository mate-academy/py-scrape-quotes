import requests
import csv

from bs4 import BeautifulSoup

from dataclasses import dataclass


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_quote(quote_soup: BeautifulSoup) -> Quote:
    tags = [tag.text for tag in quote_soup.select(".tags .tag")]
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=tags,
    )


def get_quotes() -> list[Quote]:
    quotes = []
    url = BASE_URL

    while url:
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")

        quotes_soup = soup.select(".quote")
        quotes.extend(
            [
                parse_quote(quote_soup)
                for quote_soup in quotes_soup
            ]
        )

        next_button = soup.select_one(".next > a")
        url = BASE_URL + next_button["href"] if next_button else None

    return quotes


def add_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(
        output_csv_path,
        mode="w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, list(quote.tags)])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    add_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
