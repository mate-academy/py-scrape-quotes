import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# BASE_URL = "https://quotes.toscrape.com/"


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]
    base_url = "https://quotes.toscrape.com/"

    @classmethod
    def content_to_soup(cls, url: str) -> BeautifulSoup:
        cls.base_url = url
        content = requests.get(url).content
        return BeautifulSoup(content, "html.parser")


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(text=quote_soup.select_one("span.text").text,
                 author=quote_soup.select_one(".author").text,
                 tags=[tag.text.strip() for tag in quote_soup.select(".tag")],
                 )


def parse_single_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> [Quote]:
    quotes = []
    data_soup = Quote.content_to_soup(Quote.base_url)
    logging.info("Start parsing...")
    quotes.extend(parse_single_page(data_soup))
    pagination = data_soup.select_one(".pager")
    if pagination is None:
        return quotes
    page_num = 2
    while True:
        url = urljoin(Quote.base_url, f"/page/{page_num}")
        page_soup = Quote.content_to_soup(url)
        quotes.extend(parse_single_page(page_soup))
        page_num += 1
        next_page = page_soup.select_one(".next")
        if not next_page:
            logging.info(f"That's all, thanks), "
                         f"page {page_num} was the last one")
            return quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
