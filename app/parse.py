import csv
from dataclasses import dataclass, fields
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")])


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quote() -> [Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(soup)
    next_page_link = soup.select_one(".next > a")

    while next_page_link:
        next_page_url = next_page_link["href"]
        if not next_page_url.startswith("http"):
            next_page_url = BASE_URL + next_page_url
        next_page = requests.get(next_page_url).content
        soup = BeautifulSoup(next_page, "html.parser")
        all_quotes += get_single_page_quotes(soup)

        next_page_link = soup.select_one(".next > a")

    return all_quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        for quote in quotes:
            writer.writerow(getattr(quote, field) for field in QUOTE_FIELDS)


def main(output_csv_path: str) -> None:
    quotes = get_quote()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
