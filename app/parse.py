import csv
import logging
import sys
from urllib import parse
from dataclasses import dataclass, fields, asdict

import requests
from bs4 import BeautifulSoup


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def run_parsing_quotes_with_pagination() -> list[Quote]:
    logging.info(f"We run fast parsing quotes from {URL} with pagination")
    list_quote = []
    num_page = 1
    while True:
        url = parse.urljoin(URL, f"page/{num_page}")
        quotes = get_quotes_from_single_page(url)
        if quotes is None:
            logging.info("No quotes found in this page. Save data to csv")
            break
        list_quote.extend(quotes)
        logging.info(f"Parsed {num_page} page")
        num_page += 1
    return list_quote


def get_quotes_from_single_page(url: str) -> list[Quote] | None:
    soup = BeautifulSoup(get_html_text(url), "html.parser")

    if soup.body and "No quotes found!" in soup.get_text():
        return None

    quotes = []
    for quote in soup.select(".quote"):
        quotes.append(Quote(
            text=quote.select_one(".text").text,
            author=quote.select_one(".author").text,
            tags=[tag.text for tag in quote.select(".tag")]
        ))
    return quotes


def get_html_text(url: str) -> str:
    try:
        response = requests.get(url=url)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        logging.warning(e)


def main(output_csv_path: str) -> None:
    with open(
            output_csv_path,
            mode="w",
            newline="",
            encoding="utf-8"
    ) as csvfile:
        fieldnames = [field.name for field in fields(Quote)]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        # Get quotes from parsing the pages
        quotes = run_parsing_quotes_with_pagination()
        for quote in quotes:
            quote_dict = asdict(quote)

            # Convert the list to a string that looks like a Python list
            quote_dict["tags"] = str(quote_dict["tags"])

            writer.writerow(quote_dict)


if __name__ == "__main__":
    main("quotes.csv")
