import csv
from dataclasses import dataclass, astuple

import requests
from bs4 import BeautifulSoup, element

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def _parse_single_quote(quote: element.Tag) -> Quote:
    return Quote(
        text=quote.select_one("span.text").text,
        author=quote.select_one("span > small.author").text,
        tags=[tag.text.strip() for tag in quote.select("div.tags > a.tag")],
    )


def _get_single_page(page: bytes) -> list[Quote]:
    soup = BeautifulSoup(page, "html.parser")
    quotes = soup.select("div.quote")
    return [_parse_single_quote(quote) for quote in quotes]


def get_all_pages() -> list[Quote]:
    page_number = 1
    all_page_quotes = []
    while True:
        page = requests.get(BASE_URL + f"/page/{page_number}/")
        if page.status_code != 200:
            break
        page_number += 1
        single_page_quotes = _get_single_page(page.content)
        if not single_page_quotes:
            break
        all_page_quotes.extend(single_page_quotes)
    return all_page_quotes


def write_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["text", "author", "tags"])
        csv_writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_pages()
    write_to_csv(quotes=quotes, output_csv_path=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
