import csv
import requests

from dataclasses import dataclass, astuple, fields
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com"


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
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_next_page_url(page_soup: Tag) -> str | None:
    next_page_url = page_soup.select_one("li.next a")

    if next_page_url is None:
        return None

    return BASE_URL + next_page_url["href"]


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> list[Quote]:
    url: str | None = BASE_URL
    all_quotes: list[Quote] = []

    while url is not None:
        text = requests.get(url).content
        page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(page_soup))
        url = get_next_page_url(page_soup)

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
