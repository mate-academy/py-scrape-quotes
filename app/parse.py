import csv
from dataclasses import asdict, dataclass, fields
import logging
import sys

from bs4 import BeautifulSoup, Tag
import requests


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tags .tag")]
    )


def get_home_quotes(url: str = BASE_URL) -> list[Quote]:
    response = requests.get(url)
    if response.status_code == 200:
        text = response.content
        soup = BeautifulSoup(text, "html.parser")
        products = soup.select(".quote")
        return [parse_single_quote(product) for product in products]
    else:
        logging.warning(f"Failed to retrieve quotes from URL: {url}")
        return []


def get_num_pages() -> int:
    num_of_pages = 0
    i = 1
    while True:
        text = requests.get(f"{BASE_URL}page/{i}/").content
        soup = BeautifulSoup(text, "html.parser")
        if len(soup.select(".quote")) == 0:
            break
        num_of_pages += 1
        i += 1
    return num_of_pages


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    num_of_pages = get_num_pages()

    for i in range(1, num_of_pages + 1):
        logging.info(f"Start parsing page #{i}")
        page_url = f"{BASE_URL}page/{i}/"
        all_quotes.extend(get_home_quotes(page_url))
    return all_quotes


QUOTE_FIELDS = [field.name for field in fields(Quote)]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[logging.FileHandler("parser.log"),
              logging.StreamHandler(sys.stdout)])


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=QUOTE_FIELDS)
        writer.writeheader()

        for quote in quotes:
            row = asdict(quote)
            row["tags"] = str(row["tags"])
            writer.writerow(row)


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_all_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
