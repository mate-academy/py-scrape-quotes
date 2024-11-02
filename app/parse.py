import csv
from dataclasses import dataclass, astuple, fields

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> [Quote]:
    page_num = 1
    all_quotes = []

    while True:
        page = requests.get(f"{BASE_URL}/page/{page_num}").content
        page_soup = BeautifulSoup(page, "html.parser")

        quotes = get_single_page_quotes(page_soup)
        all_quotes.extend(quotes)

        if not any("next" in page_link["class"] for page_link in
                   page_soup.select(".pager > li")):
            break

        page_num += 1

    return all_quotes


def write_quotes_to_csv_file(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv_file(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
