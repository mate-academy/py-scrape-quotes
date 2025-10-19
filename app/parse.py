import csv
import logging
import time
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"

logging.basicConfig(level=logging.INFO)


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:
    tags_list = [tag.text.strip() for tag in quote.select(".tags a.tag")]
    return Quote(
        text=quote.select_one(".text").text.strip(),
        author=quote.select_one(".author").text.strip(),
        tags=tags_list,
    )


def get_quotes_from_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def has_next_page(page_soup: BeautifulSoup) -> bool:
    next_button = page_soup.select_one(".pager .next")
    return next_button is not None


def get_all_quotes() -> list[Quote]:
    logging.info("Start parsing quotes")

    all_quotes = []
    page_num = 1

    while True:
        if page_num == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}page/{page_num}/"
            time.sleep(0.5)

        logging.info(f"Parsing page #{page_num}")
        response = requests.get(url)
        page_soup = BeautifulSoup(response.content, "html.parser")

        page_quotes = get_quotes_from_page(page_soup)
        all_quotes.extend(page_quotes)

        if not has_next_page(page_soup):
            break

        page_num += 1

    logging.info(f"Total quotes collected: {len(all_quotes)}")
    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])

    logging.info(f"Saved {len(quotes)} quotes to {output_csv_path}")


if __name__ == "__main__":
    main("quotes.csv")
