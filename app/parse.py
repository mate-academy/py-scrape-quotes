import csv
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
URL_PAGE = urljoin(BASE_URL, "page/")


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags > a")]
    )


def parse_single_page_qoutes(quote_soup: BeautifulSoup) -> list[Quote]:
    quotes = quote_soup.select(".quote")

    return [parse_single_quote(quote) for quote in quotes]


def get_list_quote() -> list[Quote]:
    all_quotes = []
    page_number = 1

    while True:
        url = f"{URL_PAGE}{page_number}"
        print(f"Start parse page #{page_number}")
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = parse_single_page_qoutes(soup)

        if not quotes:
            break

        all_quotes.extend(quotes)
        page_number += 1

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        written = csv.writer(file)
        written.writerow(["text", "author", "tags"])
        for quote in quotes:
            written.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_list_quote()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
