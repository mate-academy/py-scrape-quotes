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


FIELDS = [field.name for field in fields(Quote)]


def get_quote_tags(soup: BeautifulSoup) -> list[str]:
    tags_soup = soup.select(".tag")

    return [tag.text for tag in tags_soup]


def parse_single_quote(soup: BeautifulSoup) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=get_quote_tags(soup)
    )


def get_quotes_from_single_page(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select("div.col-md-8 > .quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def next_page_exists(page_soup: BeautifulSoup) -> bool:
    return bool(
        page_soup.select("ul.pager > li.next")
    )


def get_all_quotes():
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    next_page_num = 2

    print("Parsing page #1")
    all_quotes = get_quotes_from_single_page(first_page_soup)
    current_page_soup = first_page_soup

    while True:
        if next_page_exists(current_page_soup):
            page = requests.get(
                BASE_URL + "page/" + f"{next_page_num}"
            ).content
            print(f"Parsing page #{next_page_num}")
            current_page_soup = BeautifulSoup(page, "html.parser")
            all_quotes.extend(get_quotes_from_single_page(current_page_soup))
            next_page_num += 1
        else:
            break

    return all_quotes


def write_quotes_to_csv(path: str, quotes: list[Quote]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(FIELDS)
        writer.writerows([astuple(q) for q in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("result.csv")
