from dataclasses import dataclass
from pprint import pprint

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "http://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(single_quote: Tag) -> Quote:
    single_quote_data = dict(
        text=single_quote.select_one("span.text").text,
        author=single_quote.select_one(".author").text,
        tags=[tag.text for tag in single_quote.find_all("a", class_="tag")]
    )
    return Quote(**single_quote_data)


def parse_quotes_of_one_page() -> list[Quote]:
    page_content = requests.get(BASE_URL).content
    base_soup = BeautifulSoup(page_content, "html.parser")

    page_quotes_soup = base_soup.select(".quote")
    print(page_quotes_soup)

    all_page_quotes = [
        parse_single_quote(single_quote) for single_quote in page_quotes_soup
    ]
    pprint(all_page_quotes)

    return all_page_quotes


def parse_all_quotes():
    page_content = requests.get(BASE_URL).content
    base_soup = BeautifulSoup(page_content, "html.parser")

    page_quotes_soup = base_soup.select(".quote")
    print(page_quotes_soup)

    all_page_quotes = [
        parse_single_quote(single_quote) for single_quote in page_quotes_soup
    ]
    pprint(all_page_quotes)

    return all_page_quotes


def main(output_csv_path: str) -> None:
    parse_quotes_of_one_page()


if __name__ == "__main__":
    main("quotes.csv")
