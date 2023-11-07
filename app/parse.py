import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    tags = []
    for tag in quote_soup.select(".tag"):
        tags.append(tag.text)
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=tags
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = []
    num_page = 1

    while soup.select_one(".next"):
        page = urljoin(BASE_URL, f"/page/{num_page}/")
        page = requests.get(page).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        num_page += 1

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:

    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)

        writer.writerow(QUOTE_FIELDS)

        for quote in quotes:
            writer.writerow(astuple(quote))


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
