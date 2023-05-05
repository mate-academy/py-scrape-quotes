import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, Tag

URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")


def get_single_quote(quote: Tag) -> Quote:
    text = quote.select_one("span.text").text
    author = quote.select_one("small.author").text
    tags = [tag.text for tag in quote.select("div.tags a")]
    return Quote(text=text, author=author, tags=tags)


def get_quotes(url: str) -> list[Quote]:
    page_number = 1
    next_button = True
    quotes = []

    while next_button:
        page_url = f"{url}/page/{page_number}/"
        soup = get_soup(page_url)
        quotes_html = soup.select("div.quote")
        quotes += [get_single_quote(quote) for quote in quotes_html]

        next_button = soup.select_one("li.next a")
        if not next_button:
            break

        page_number += 1

    return quotes


def write_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_quotes(URL)
    write_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
