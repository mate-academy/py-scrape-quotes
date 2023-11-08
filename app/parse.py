import csv
from dataclasses import dataclass, astuple, fields

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_all_tags(quote_soup: BeautifulSoup) -> list[str]:
    return [tag.text for tag in quote_soup.select(".tag")]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one("span.text").text,
        author=quote_soup.select_one(".author").text,
        tags=get_all_tags(quote_soup)
    )


def get_num_pages() -> int:
    num_pages = 1
    page = requests.get(BASE_URL + f"/page/{num_pages}").content
    soup = BeautifulSoup(page, "html.parser")
    pagination = soup.select_one("li.next")

    while pagination:
        num_pages += 1
        page = requests.get(BASE_URL + f"/page/{num_pages}").content
        soup = BeautifulSoup(page, "html.parser")
        pagination = soup.select_one("li.next")

    return num_pages


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> list[Quote]:
    first_page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(first_page, "html.parser")

    quotes = get_single_page_quotes(first_page_soup)

    num_pages = get_num_pages()

    for num_page in range(2, num_pages + 1):
        page = requests.get(BASE_URL + f"/page/{num_page}").content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(get_single_page_quotes(soup))

    return quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
