import sys
from dataclasses import dataclass, fields, astuple

import logging
import requests
from bs4 import BeautifulSoup, Tag, ResultSet
import csv


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def main(output_csv_path: str) -> None:
    logging.info("Start parsing")
    all_quotes = scrape_quotes()
    write_quotes_to_csv(output_csv_path, all_quotes)


def scrape_quotes() -> list[Quote]:
    all_quotes = []
    curr_page = 1
    has_next_page = True
    while has_next_page:
        logging.info(f"Page: {curr_page}")
        response = requests.get(
            f"https://quotes.toscrape.com/page/{curr_page}/"
        ).text
        soup = BeautifulSoup(response, "html.parser")
        quotes = soup.select(".quote")
        quotes = create_quotes(quotes)
        all_quotes.extend(quotes)
        if len(quotes) != 10:
            has_next_page = False
        else:
            curr_page += 1

    return all_quotes


def create_quotes(quotes: ResultSet[Tag]) -> list[Quote]:
    quote_list = []
    for quote in quotes:
        text = quote.select_one(".text").text
        author = quote.select_one(".author").text
        tags = [tag.text for tag in quote.select_one(".tags").select(".tag")]
        quote_list.append(Quote(text=text, author=author, tags=tags))

    return quote_list


def write_quotes_to_csv(path: str, quotes: list[Quote]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(QUOTES_FIELDS)
        csv_writer.writerows([astuple(quote) for quote in quotes])

    logging.info(f"Written to {path}")


if __name__ == "__main__":
    main("quotes.csv")
