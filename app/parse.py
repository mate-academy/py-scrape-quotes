import requests
import csv
import time
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass, fields, astuple


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select("a.tag")],
    )


def get_single_page_quotes(soup: Tag) -> [Quote]:
    """parse all element in one page"""
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> [Quote]:
    """Return all quotes from all pages"""
    all_quotes = []
    current_page_url = BASE_URL

    while current_page_url:
        response = requests.get(current_page_url)
        soup = BeautifulSoup(response.content, "html.parser")

        all_quotes.extend(get_single_page_quotes(soup))

        next_page = soup.select_one(".next > a")
        if next_page:
            current_page_url = BASE_URL + next_page["href"]
            time.sleep(1)
        else:
            current_page_url = None

    return all_quotes


def write_quotes_to_csv(quotes: [Quote], path: str) -> None:
    """Save quotes to CSV file"""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
