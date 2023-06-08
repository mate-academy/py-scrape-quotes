import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
import requests_cache
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
SESSION = requests_cache.CachedSession("demo_cache")

logging.basicConfig(
    level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)]
)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def write_author_to_csv(author_name: str, description: str) -> None:
    with open("authors.csv", "a") as file:
        writer = csv.writer(file)
        writer.writerow((author_name, description))


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    quote = Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one("small.author").text,
        tags=[wrapper.text for wrapper in quote_soup.select("a.tag")],
    )

    author_page = SESSION.get(
        urljoin(
            BASE_URL,
            f"/author/{quote.author.replace('.', '').replace(' ', '-')}/",
        )
    ).content
    author_soup = BeautifulSoup(author_page, "html.parser")
    description = (
        author_soup.select_one(".author-description")
        .text.strip()
        .replace("“", "")
    )
    write_author_to_csv(quote.author, description)

    return quote


def parse_page(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    quotes_class_list = []

    for quote in quotes:
        quotes_class_list.append(parse_single_quote(quote))

    return quotes_class_list


def write_quotes_to_csv(quotes: [Quote], csv_path: str) -> None:
    with open(csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")
    logging.info(msg="Start parsing page #1")

    with open("authors.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(["author_name", "description"])

    all_quotes = parse_page(first_page_soup)

    num_page = 2
    while True:
        page = requests.get(urljoin(BASE_URL, f"/page/{num_page}/")).content
        page_soup = BeautifulSoup(page, "html.parser")

        if page_soup.find_all(lambda tag: "No quotes found!" in tag.text):
            break

        logging.info(msg=f"Start parsing page #{num_page}")
        all_quotes.extend(parse_page(page_soup))
        num_page += 1

    write_quotes_to_csv(all_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
