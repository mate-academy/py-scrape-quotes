from dataclasses import (
    dataclass,
    fields,
    astuple
)
from bs4 import BeautifulSoup
import csv
import requests


BASE_URL = "https://quotes.toscrape.com/"
TEXT_P = ".text"
AUTHOR_P = ".author"
ONE_TAG_P = ".tags > a.tag"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(TEXT_P).text,
        author=quote_soup.select_one(AUTHOR_P).text,
        tags=[tag.text for tag in quote_soup.select(ONE_TAG_P)],
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes(current_url: str) -> [Quote]:
    all_quotes = []

    while current_url:
        page = requests.get(current_url)
        page_soup = BeautifulSoup(page.content, "html.parser")

        all_quotes.extend(get_single_page_quotes(page_soup))
        next_page = page_soup.select_one(".next > a")
        if next_page:
            next_page_href = next_page["href"]
            current_url = BASE_URL + next_page_href
        else:
            current_url = None

    return all_quotes


def write_quotes_to_csv(quotes: [Quote], output_path: str) -> None:
    with open(output_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_path: str) -> None:
    quotes = get_all_quotes(BASE_URL + "/page/1/")
    write_quotes_to_csv(quotes, output_path)


if __name__ == "__main__":
    main("quotes.csv")
