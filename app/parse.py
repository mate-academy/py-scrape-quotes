import csv
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

import requests
from urllib.parse import urljoin


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"

QUOTES_OUTPUT_CSV_PATH = "quotes.csv"


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.get_text() for tag in quote_soup.select(".tag")]
    )


def get_information_from_single_page(quote_soup: BeautifulSoup) -> [Quote]:
    quotes = quote_soup.select(".quote")

    return [parse_single_quote(quote) for quote in quotes]


def get_quotes_from_site() -> [Quote]:
    first_page = requests.get(BASE_URL).content
    first_soup = BeautifulSoup(first_page, "html.parser")

    all_quotes: list = get_information_from_single_page(first_soup)

    first_next_button = first_soup.find("li", class_="next")

    if first_next_button:
        num_of_page = 2

        while True:
            url = urljoin(BASE_URL, f"page/{num_of_page}/")
            page = requests.get(url).content
            soup = BeautifulSoup(page, "html.parser")
            quote = get_information_from_single_page(soup)
            if quote:
                all_quotes.extend(quote)
                num_of_page += 1
            else:
                break

    return all_quotes


def write_quotes_to_csv(path_to_csv_file: str, quotes: [Quote]) -> None:
    with open(path_to_csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow(
                [quote.text, quote.author, quote.tags]
            )


def main(output_csv_path: str) -> None:
    quotes = get_quotes_from_site()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
