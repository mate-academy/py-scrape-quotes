import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"
PAGE_URL = f"{BASE_URL}/page/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def check_next_page_exists(page_soup: BeautifulSoup) -> bool:
    next_link = page_soup.select_one(".next a")

    return next_link is not None


def get_all_tags(quote_soup: Tag) -> [str]:
    tags_elements = quote_soup.select(".tag")

    return [element.text for element in tags_elements]


def parse_single_quote(quote_soup: Tag) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = get_all_tags(quote_soup)

    return Quote(
        text=text,
        author=author,
        tags=tags
    )


def parse_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote) for quote in quotes]


def parse_page(page_number: int) -> ([Quote], bool):
    url = f"{PAGE_URL}/{page_number}"
    current_page = requests.get(url).content

    soup = BeautifulSoup(current_page, "html.parser")

    quotes = parse_quotes(soup)

    next_page_exists = check_next_page_exists(soup)

    return quotes, next_page_exists


def get_all_quotes() -> [Quote]:
    quotes = []

    next_page_exists = True
    page_number = 1

    while next_page_exists:
        page_quotes, next_page_exists = parse_page(page_number)

        quotes.extend(page_quotes)
        page_number += 1

    return quotes


def write_quotes_to_the_file(quotes: list[Quote], file_name: str) -> None:
    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            tags_string = repr(quote.tags)
            writer.writerow([quote.text, quote.author, tags_string])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    write_quotes_to_the_file(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
