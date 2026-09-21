from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup, Tag
import requests
import csv


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
        tags=[tag.text for tag in quote.select(".tags .tag")],
    )


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    return [parse_single_quote(q) for q in page_soup.select(".quote")]


def quotes() -> list[Quote]:
    """Scrape quotes from all pages, following the Next link."""
    all_quotes = []
    page = 1
    while True:
        text = requests.get(f"{BASE_URL}page/{page}/").content
        soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        if soup.select_one("li.next") is None:
            break
        page += 1
    return all_quotes


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
