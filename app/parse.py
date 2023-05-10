import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin


import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]

    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:
    page_num = 1
    all_quotes = []
    while True:
        param = f"page/{page_num}/"
        home_url = urljoin(BASE_URL, param)
        page = requests.get(home_url).content
        page_soup = BeautifulSoup(page, "html.parser")

        all_quotes += get_single_page_quotes(page_soup)
        if not page_soup.select(".next"):
            break
        page_num += 1

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], path: str) -> None:
    with open(path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
