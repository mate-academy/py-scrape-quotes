import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup

HOME_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


FIELDS = [field.name for field in fields(Quote)]


def get_phrazes(phraze_soup: BeautifulSoup):
    return Quote(
        text=phraze_soup.select_one(".text").text,
        author=phraze_soup.select_one(".author").text,
        tags=[
            tag.text for tag in phraze_soup.select(".tag")
        ]
    )


def get_single_page_phrazes(soup):
    phrazes = soup.select(".quote")

    return [
        get_phrazes(phraze) for phraze in phrazes
    ]


def get_all_quotes() -> [Quote]:
    page = requests.get(HOME_URL).content
    soup = BeautifulSoup(page, "html.parser")
    all_phrazes = get_single_page_phrazes(soup)
    page_num = 2

    while True:
        if soup.select(".next"):
            page = requests.get(f"{HOME_URL}page/{page_num}/").content
            soup = BeautifulSoup(page, "html.parser")
            all_phrazes.extend(get_single_page_phrazes(soup))
            page_num += 1
        else:
            break

    return all_phrazes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
