import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTER_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quoter(quoter_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quoter_soup.select_one(".text").text,
        author=quoter_soup.select_one(".author").text,
        tags=(quoter_soup.select_one(".tags").
              text.replace(" ", "").split("\n")[3:-1])
    )


def get_single_page(page_soup: BeautifulSoup) -> [Quote]:
    quotes_of_page = page_soup.select(".quote")
    return [parse_single_quoter(quoter_soup) for quoter_soup in quotes_of_page]


def get_home_product() -> [Quote]:
    num_page = 2
    url = BASE_URL
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    all_page = get_single_page(soup)
    while soup.select_one("nav li.next") is not None:
        page = requests.get(BASE_URL + f"page/{num_page}").content
        soup = BeautifulSoup(page, "html.parser")
        all_page.extend(get_single_page(soup))
        num_page += 1
    return all_page


def write_quoter_to_csv_path(quoters: [Quote], file_name: str) -> None:
    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTER_FIELDS)
        writer.writerows([astuple(quoter) for quoter in quoters])


def main(output_csv_path: str) -> None:
    quoter = get_home_product()
    write_quoter_to_csv_path(quoter, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
