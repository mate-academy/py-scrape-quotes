import csv
from dataclasses import dataclass, astuple
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag

import requests

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_num_page() -> int:
    num_page = 1

    status_code = requests.get(BASE_URL).status_code

    while status_code == 200:
        page = requests.get(urljoin(BASE_URL, f"page/{num_page}/")).content
        soup = BeautifulSoup(page, "html.parser")

        next_button = soup.find("li", {"class": "next"})

        if next_button:
            num_page += 1
        else:
            break

    return num_page


def parse_quote_page(soup: Tag) -> Quote:

    text = getattr(soup.select_one(".text"), "text", "")
    author = getattr(soup.select_one(".author"), "text", "")
    tags = [quote.text for quote in soup.select(".tag")]\
        if soup.select(".tags") else []

    return Quote(text, author, tags)


def parse_single_quote(quote_soup: BeautifulSoup) -> [Quote]:
    page = quote_soup.select(".quote")

    return [parse_quote_page(quote) for quote in page]


def parse_all_quote() -> [Quote]:
    num_page = get_num_page()

    all_quotes = []

    for page in range(num_page + 1):
        page_quote = requests.get(urljoin(BASE_URL, f"page/{page}")).content
        soup = BeautifulSoup(page_quote, "html.parser")

        all_quotes.extend(parse_single_quote(soup))

    return all_quotes


def write_data_in_cv_file(cs_file: str) -> None:
    with open(cs_file, "w", newline="", encoding="utf-8") as file:
        quotes = parse_all_quote()
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_data_in_cv_file(output_csv_path)


if __name__ == "__main__":
    main("correct_quotes.csv")
