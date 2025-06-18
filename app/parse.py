import csv
from dataclasses import dataclass, fields, astuple
from typing import Generator
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_page(page: BeautifulSoup) -> list[Quote]:
    quotes = []
    quote_cards = page.find_all("div", class_="quote")
    for quote_card in quote_cards:
        text = quote_card.select_one(".text").text
        author = quote_card.select_one(".author").text
        tags = [tag.text for tag in quote_card.find_all("a", class_="tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))
    return quotes


def fetch_page_content(url: str) -> bytes | None:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(e)


def page_generator(url: str) -> Generator[BeautifulSoup, None, None]:
    page_counter = 1
    while True:
        page_url = urljoin(url, f"page/{page_counter}/")
        content = fetch_page_content(page_url)
        if content is None:
            break
        page = BeautifulSoup(content, "lxml")
        col_md_8_elements = page.select(".col-md-8")
        if len(col_md_8_elements) < 2:
            break
        no_quotes_div = page.select(".col-md-8")[1]
        if "No quotes found!" in no_quotes_div.get_text(strip=True):
            break
        yield page
        page_counter += 1


def get_quotes() -> list[Quote]:
    result = []
    for page in tqdm(page_generator(BASE_URL)):
        result.extend(parse_page(page))
    return result


def write_products_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_products_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
