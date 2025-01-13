import csv

import requests
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass, fields, astuple

from requests import Response

URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_pages(url: str) -> Response:
    page_num = 1
    while True:
        response = requests.get(f"{url}/page/{page_num}/")
        if b"No quotes found!" in response.content:
            break
        page_num += 1
        yield response.content


def write_to_csv(quotes: list[Quote], file_name: str) -> None:
    with open(file_name, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def extract_quote(tag: Tag) -> Quote:
    return Quote(
        text=tag.select_one("span.text").text,
        author=tag.select_one("small.author").text,
        tags=[t.text for t in tag.select("a.tag")],
    )


def scrap_quotes(page_content: bytes) -> list[Quote]:
    soup = BeautifulSoup(page_content, "html.parser")
    quote_tags = soup.select(".quote")
    return [extract_quote(tag) for tag in quote_tags]


def scrape_pages() -> list[Quote]:
    quotes = []
    for page in get_pages(URL):
        quotes.extend(scrap_quotes(page))
    return quotes


def main(output_csv_path: str) -> None:
    quotes = scrape_pages()
    write_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
