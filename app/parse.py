import csv
from dataclasses import dataclass, astuple, fields

import requests
from bs4 import BeautifulSoup, Tag

URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELD = [field.name for field in fields(Quote)]


def create_quote_object(soup: Tag) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=[tag.text for tag in soup.select(".tags > a")]
    )


def get_single_data(page_soup: BeautifulSoup) -> list:
    quotes = page_soup.select(".quote")
    return [create_quote_object(page) for page in quotes]


def get_data() -> list:
    next_url_to_scrape = URL
    all_quotes = []

    while next_url_to_scrape:
        page = requests.get(next_url_to_scrape).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_data(soup))

        try:
            next_url_to_scrape = URL + soup.select_one(
                ".next > a[href]"
            )["href"]
        except TypeError:
            next_url_to_scrape = False

    return all_quotes


def write_products_to_csv(qoutes: [Quote], path: str) -> None:
    with open(path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELD)
        writer.writerows([astuple(qoute) for qoute in qoutes])


def main(output_csv_path: str) -> None:
    data = get_data()
    write_products_to_csv(data, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
