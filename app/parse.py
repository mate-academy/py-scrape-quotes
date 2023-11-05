import csv
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
URL_PAGE = urljoin(BASE_URL, "page/")


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_qoute(qoute_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=qoute_soup.select_one(".text").text,
        author=qoute_soup.select_one(".author").text,
        tags=[tag.text for tag in qoute_soup.select(".tags > a")]
    )


def parse_single_page_qoutes(quote_soup: BeautifulSoup) -> [Quote]:
    qoutes = quote_soup.select(".quote")
    if qoutes:
        return [parse_single_qoute(qoute) for qoute in qoutes]


def get_list_quote() -> [Quote]:
    all_qoutes = []
    page_number = 1

    while True:
        url = f"{URL_PAGE}{page_number}"
        print(f"Start parse page #{page_number}")
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        qoutes = parse_single_page_qoutes(soup)

        if not qoutes:
            break

        all_qoutes.extend(qoutes)
        page_number += 1

    return all_qoutes


def write_qoutes_to_csv(qoutes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        written = csv.writer(file)
        written.writerow(["text", "author", "tags"])
        for qoute in qoutes:
            written.writerow([qoute.text, qoute.author, qoute.tags])


def main(output_csv_path: str) -> None:
    qoutes = get_list_quote()
    write_qoutes_to_csv(qoutes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
