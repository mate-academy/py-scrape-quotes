import csv
from dataclasses import dataclass, fields

import requests
from bs4 import BeautifulSoup

MAIN_PAGE_URL = "http://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_quotes(response: bytes) -> [Quote]:
    soup = BeautifulSoup(response, "html.parser")
    quotes = soup.select(".quote")

    return [create_quote(quote) for quote in quotes]


def create_quote(soup: BeautifulSoup) -> Quote:
    tags = soup.select_one(".keywords")["content"].split(",")
    if "" in tags:
        tags.clear()

    return Quote(
        text=soup.select_one(".text").text.replace("вЂњ", ""),
        author=soup.select_one(".author").text,
        tags=tags,
    )


def get_all_quotes_from_pages() -> [Quote]:
    response = requests.get(MAIN_PAGE_URL).content
    quotes = get_quotes(response)
    for i in range(2, 11):
        response = requests.get(MAIN_PAGE_URL + "/page/" + f"{i}/").content
        quotes.extend(get_quotes(response))
    return quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(
            [
                (quote.text, quote.author, quote.tags)
                for quote in get_all_quotes_from_pages()
            ]
        )


if __name__ == "__main__":
    main("quotes.csv")
