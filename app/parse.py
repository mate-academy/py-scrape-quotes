from dataclasses import dataclass
from urllib.parse import urljoin
from dataclass_csv import DataclassWriter
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_page(url: str, quotes: list[Quote]):
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    quotes_on_page = soup.select(".quote")
    for quote in quotes_on_page:
        quote1 = Quote(
            text=quote.select_one(".text").text,
            author=quote.select_one(".author").text,
            tags=[tag.text for tag in quote.select(".tag")],
        )
        quotes.append(quote1)

    if soup.select_one(".next > a") is not None:
        parse_single_page(
            urljoin(BASE_URL, soup.select_one(".next > a")["href"]),
            quotes
        )


def main(output_csv_path: str) -> None:
    quote_list = []
    parse_single_page(BASE_URL, quote_list)
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        w = DataclassWriter(f, quote_list, Quote)
        w.write()


if __name__ == "__main__":
    main("quotes.csv")
