import csv
import logging
import sys
from urllib import parse
from dataclasses import dataclass, fields, asdict
import time
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


def get_html_text(url: str) -> str | None:
    try:
        response = requests.get(url=url)
        if response.status_code == 200:
            return response.text
        logging.warning(f"Failed to get page {url}, status code: {response.status_code}")
    except Exception as e:
        logging.warning(f"Exception during request to {url}: {e}")
    return None


def get_quotes_from_single_page(url: str) -> list[Quote] | None:
    html = get_html_text(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    quote_divs = soup.select(".quote")
    if not quote_divs:
        return None

    quotes = []
    for quote in quote_divs:
        quotes.append(Quote(
            text=quote.select_one(".text").text,
            author=quote.select_one(".author").text,
            tags=[tag.text for tag in quote.select(".tag")]
        ))
    return quotes


def run_parsing_quotes_with_pagination() -> list[Quote]:
    logging.info(f"Start parsing quotes from {URL} with pagination")
    list_quote = []
    num_page = 1
    while True:
        url = parse.urljoin(URL, f"page/{num_page}/")
        quotes = get_quotes_from_single_page(url)
        if not quotes:
            logging.info("No quotes found. Finished parsing.")
            break
        list_quote.extend(quotes)
        logging.info(f"Parsed page {num_page}")
        num_page += 1
        time.sleep(1)  # Будем бережно обращаться к серверу
    return list_quote


def main(output_csv_path: str) -> None:
    quotes = run_parsing_quotes_with_pagination()

    with open(
        output_csv_path,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as csvfile:
        fieldnames = [field.name for field in fields(Quote)]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for quote in quotes:
            quote_dict = asdict(quote)
            quote_dict["tags"] = str(quote_dict["tags"])  # Сохраняем теги как строку
            writer.writerow(quote_dict)


if __name__ == "__main__":
    main("quotes.csv")
