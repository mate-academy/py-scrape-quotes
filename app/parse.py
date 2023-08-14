import csv
from dataclasses import dataclass, astuple, fields

import requests
from bs4 import BeautifulSoup

HOME_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def get_single_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:
    first_page = requests.get(HOME_URL).content
    first_soup = BeautifulSoup(first_page, "html.parser")

    num_pages = get_num_pages(first_soup)
    all_quotes = get_single_page(first_soup)

    next_page = 1
    while num_pages == 1:
        next_page += 1
        page = requests.get(HOME_URL + f"page/{next_page}/").content
        soup = BeautifulSoup(page, "html.parser")
        num_pages = get_num_pages(soup)
        all_quotes += get_single_page(soup)
    return all_quotes


def get_num_pages(page_soup: BeautifulSoup) -> int | None:
    try:
        pagination_next = page_soup.select_one("li.next").text
    except AttributeError:
        return 0

    if pagination_next is None:
        return None
    return 1


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text ").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def write_products_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_products_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
