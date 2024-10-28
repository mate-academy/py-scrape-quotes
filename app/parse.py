import csv
from dataclasses import dataclass, fields

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_single_page_quote(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_num_pages() -> int:
    pages = 1
    while True:
        page_url = f"{BASE_URL}page/{pages}/"

        response = requests.get(page_url)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, "html.parser")

        next_page = soup.select_one(".next a")
        if not next_page:
            break

        pages += 1

    return pages


def get_all_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    num_pages = get_num_pages()

    all_quotes = get_single_page_quote(first_page_soup)

    for page_num in range(2, num_pages + 1):
        page = requests.get(f"{BASE_URL}page/{page_num}/").content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quote(soup))

    return all_quotes


def write_quotes(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_quotes_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes(output_csv_quotes_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
