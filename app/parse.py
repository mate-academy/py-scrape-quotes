import csv
from dataclasses import dataclass, astuple, fields
from bs4 import Tag, BeautifulSoup
import requests


QUOTES_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text.replace("”", "").replace("“", ""),
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_page_quotes() -> list[Quote]:
    all_quotes = []
    current_url = QUOTES_URL

    while current_url:
        response = requests.get(current_url)
        page_soup = BeautifulSoup(response.content, "html.parser")
        all_quotes.extend(get_single_page_quotes(page_soup))
        next_page = page_soup.select_one(".pager .next a")
        if next_page:
            current_url = QUOTES_URL + next_page["href"].lstrip("/")
        else:
            current_url = None

    return all_quotes


def write_quotes_to_csv(file_name: str, quotes: list[Quote]) -> None:
    with open(file_name, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(output_csv_path, get_page_quotes())


if __name__ == "__main__":
    main("quotes.csv")
