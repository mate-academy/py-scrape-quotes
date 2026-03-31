import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import Tag, BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text.strip(),
        author=quote.select_one(".author").text.strip(),
        tags=[tag.text.strip() for tag in quote.select(".tag")],
    )


def get_single_page_quotes(quote_soup: Tag) -> list[Quote]:
    quotes = quote_soup.select(".quote")
    return [parse_single_quote(q) for q in quotes]


def get_quotes_from_all_pages() -> list[Quote]:
    text = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(text, "html.parser")
    quotes = get_single_page_quotes(first_page_soup)

    next_page_link = first_page_soup.select_one(".pager li.next")
    num_page = 2
    while next_page_link:
        url = urljoin(BASE_URL, f"page/{num_page}/")
        num_page += 1
        text = requests.get(url).content
        next_page_soup = BeautifulSoup(text, "html.parser")
        quotes.extend(get_single_page_quotes(next_page_soup))
        next_page_link = next_page_soup.select_one(".pager li.next")

    return quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]):
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(output_csv_path, get_quotes_from_all_pages())


if __name__ == "__main__":
    main("quotes.csv")
