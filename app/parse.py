import csv
from dataclasses import dataclass
from dataclasses import fields, astuple
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"
PAGE_URL = BASE_URL + "page/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return (Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    ))


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> list[Quote]:
    text = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(text, "html.parser")

    all_quotes = get_single_page_quotes(first_page_soup)
    page_num = 10

    for page_num in range(2, page_num + 1):
        text = requests.get(PAGE_URL + f"{page_num}/").content
        next_page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(next_page_soup))
    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    all_quotes = get_quotes()
    write_quotes_to_csv(all_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
