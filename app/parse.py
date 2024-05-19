import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELD = [field for field in fields(Quote)]


def get_num_page():
    page = 1

    while True:
        response = requests.get(urljoin(BASE_URL, f"page/{page}")).content
        soup = BeautifulSoup(response, "html.parser")

        current_page = soup.find("li", {"class": "next"})
        if current_page:
            page += 1
        else:
            break

    return page


def parse_single_quote(soup_quote: Tag) -> Quote:
    text = getattr(soup_quote.select_one(".text"), "text", "")
    author = getattr(soup_quote.select_one(".author"), "text", "")
    tags = [tag.text for tag in soup_quote.select("div.tags > .tag")] \
        if soup_quote.select("div.tags > .tag") else []

    return Quote(text=text, author=author, tags=tags)


def get_single_quote_page(page_soup: BeautifulSoup) -> [Quote]:
    page = page_soup.select(".quote")

    return [parse_single_quote(quote) for quote in page]


def get_quote() -> [Quote]:
    first_page_quote = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(first_page_quote, "html.parser")

    num_pages = get_num_page()

    all_quotes = get_single_quote_page(first_page_soup)

    for page_quote in range(2, num_pages + 1):
        page = requests.get(urljoin(BASE_URL, f"page/{page_quote}")).content
        soup = BeautifulSoup(page, "html.parser")

        all_quotes.extend(get_single_quote_page(soup))

    return all_quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELD)
        writer.writerows([astuple(quote) for quote in get_quote()])


if __name__ == "__main__":
    main("correct_quotes.csv")
