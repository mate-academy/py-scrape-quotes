import time
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup, Tag
import csv


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    keywords = quote.select_one(".keywords")
    tags = keywords.get("content", "") if keywords else ""

    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=tags.split(",") if tags else [],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> list[Quote]:
    all_quotes = []
    page_num = 1

    while True:
        response = requests.get(f"{BASE_URL}/page/{page_num}/")

        page_soup = BeautifulSoup(response.content, "html.parser")
        all_quotes.extend(get_single_page_quotes(page_soup))

        next_page = page_soup.select_one(".next")

        if next_page is None:
            break

        page_num += 1
        time.sleep(1)

    return all_quotes


def write_quotes_to_csv(
    quotes: list[Quote],
    output_csv_path: str,
) -> None:
    with open(
        output_csv_path,
        "w",
        encoding="utf-8",
        newline="",
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
