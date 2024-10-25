import csv
import logging
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, Tag


SITE_URL = "https://quotes.toscrape.com/"

logging.basicConfig(level=logging.INFO)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_one_quote(quote_tag: Tag) -> Quote:
    return Quote(
        text=quote_tag.select_one(".text").text,
        author=quote_tag.select_one(".author").text,
        tags=[tag.text for tag in quote_tag.select(".tag")]
    )


def get_all_quotes_from_page(page: Tag) -> list[Quote]:
    page_quotes = page.select(".quote")

    return [get_one_quote(quote) for quote in page_quotes]


def get_all_quotes_from_site() -> list[Quote]:
    logging.info("Start parsing!")
    site = requests.get(SITE_URL).content
    first_page = BeautifulSoup(site, "html.parser")

    quotes = get_all_quotes_from_page(first_page)

    i = 2
    while True:
        logging.info(f"Parse page №{i}")
        site = requests.get(SITE_URL + f"page/{i}/").content
        page = BeautifulSoup(site, "html.parser")

        quotes.extend(get_all_quotes_from_page(page))
        i += 1

        if not page.select_one(".next"):
            break

    return quotes


def write_quotes(output_scv_path: str, quotes: list[Quote]) -> None:
    logging.info(f"Writing all quotes to {output_scv_path} file")
    with open(output_scv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    write_quotes(output_csv_path, get_all_quotes_from_site())


if __name__ == "__main__":
    main("quotes.csv")
