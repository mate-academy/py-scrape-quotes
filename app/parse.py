import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from typing import Optional

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]
    bio: Optional[str] = None


QUOTE_FIELD = [field.name for field in fields(Quote)]

cache = dict()

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers={
        logging.StreamHandler(sys.stdout)
    }
)


def bio_parse(url: str) -> str:
    bio_page = requests.get(url).content
    bio_soup = BeautifulSoup(bio_page, "html.parser")

    bio = bio_soup.select_one(".author-description").text

    return bio


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    text = quote.select_one("span.text").text.strip()
    author = quote.select_one("span > small.author").text.strip()

    bio_url = urljoin(BASE_URL, quote.select_one("span > a")["href"])

    if bio_url not in cache:
        cache[bio_url] = bio_parse(bio_url)

    bio = cache[bio_url]

    tags = [tag.text.strip() for tag in quote.select("div.tags a")]
    return Quote(text, author, tags, bio)


def get_single_page_quote(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.find_all(class_="quote")

    return [parse_single_quote(quote) for quote in quotes]


def get_home_quotes() -> [Quote]:
    logging.info("Start parsing quotes")
    page = requests.get(BASE_URL).content
    first_page_quote = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quote(first_page_quote)

    for page_num in range(2, 100_000):
        logging.info(f"Start parsing page: {page_num}")
        page_url = urljoin(BASE_URL, f"/page/{page_num}")
        page = requests.get(page_url).content
        soup = BeautifulSoup(page, "html.parser")
        has_quote = soup.select_one(".quote")

        if has_quote is None:
            break

        all_quotes.extend(get_single_page_quote(soup))

    return all_quotes


def write_vacancies_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELD)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_home_quotes()
    write_vacancies_to_csv(quotes=quotes, output_csv_path=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
