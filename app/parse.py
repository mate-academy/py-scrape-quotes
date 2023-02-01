import csv
import requests

from urllib.parse import urljoin
from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"
DETAIL_URL = "page/{}/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[
            tag.getText()
            for tag in quote.find_all("a", "tag")
        ],
    )


def get_page(path: str) -> BeautifulSoup:
    response = requests.get(path).content
    page = BeautifulSoup(response, "html.parser")
    return page


def get_all_quotes_from_one_page(page: BeautifulSoup) -> list[Quote]:
    soup = page.select(".quote")
    return [get_single_quote(quote) for quote in soup]


def parse_all_quotes() -> list[Quote]:
    count = 1
    while True:
        page = get_page(urljoin(BASE_URL, DETAIL_URL.format(count)))
        all_page_quotes = get_all_quotes_from_one_page(page)

        yield all_page_quotes

        count += 1
        if not page.select_one(".next"):
            break


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile, lineterminator="\n")
        csvwriter.writerow(["text", "author", "tags"])
        for page in parse_all_quotes():
            for quote in page:
                csvwriter.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
