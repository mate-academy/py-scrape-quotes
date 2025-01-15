import csv
import logging
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import Tag, BeautifulSoup
from requests import Response

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def get_content(url: str) -> Response | str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while requesting {url}: {e}")
        return ""


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tags .tag")]
    )


def get_single_page_quotes(page_soup: Tag) -> [Quote]:
    quotes = page_soup.find_all(class_="quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> [Quote]:
    content = get_content(BASE_URL).content
    first_page_soup = BeautifulSoup(content, "html.parser")
    all_quotes = get_single_page_quotes(first_page_soup)
    page_count: int = 2
    while True:
        content = get_content(urljoin(BASE_URL, f"page/{page_count}")).content
        next_page_soup = BeautifulSoup(content, "html.parser")
        page_quotes = get_single_page_quotes(next_page_soup)
        if not page_quotes:
            break
        all_quotes.extend(page_quotes)
        page_count += 1
    return all_quotes


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_all_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
