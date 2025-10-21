import csv
import time
from dataclasses import dataclass, fields

import requests
from bs4 import BeautifulSoup, Tag

TIME_BETWEEN_REQUESTS = 0.5
BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_quotes(session: requests.Session) -> list[Quote]:
    page_num = 1
    response = session.get(f"{BASE_URL}/page/{page_num}", timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    quotes = soup.select(".quote")
    next_page = soup.select_one(".next")

    while next_page:
        time.sleep(TIME_BETWEEN_REQUESTS)
        page_num += 1
        response = session.get(f"{BASE_URL}/page/{page_num}", timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        quotes.extend(soup.select(".quote"))
        next_page = soup.select_one(".next")

    return [parse_quote(quote) for quote in quotes]


def write_to_csv(csv_path: str, quotes: list[Quote]) -> None:
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(
            (quote.text, quote.author, str(quote.tags)) for quote in quotes
        )


def main(output_csv_path: str) -> None:
    session = requests.Session()
    quotes = get_quotes(session)
    write_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
