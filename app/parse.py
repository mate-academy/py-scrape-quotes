from __future__ import annotations
from dataclasses import dataclass, astuple
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com/page/1/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    def parse_single_quote(self, quote_soup: BeautifulSoup) -> Quote:
        return Quote(
            text=quote_soup.select_one(".text").text,
            author=quote_soup.select_one(".author").text,
            tags=[tag.text for tag in quote_soup.select(".tags > a.tag")]
        )

    def get_product_on_page(self, quotes: BeautifulSoup) -> [Quote]:
        quotes = quotes.select(".quote")
        return [self.parse_single_quote(self, quote) for quote in quotes]

    def get_quotes(self) -> [Quote]:
        page = requests.get(BASE_URL).content
        soup = BeautifulSoup(page, "html.parser")
        next_page = self.get_next_page(self, soup)
        quotes = self.get_product_on_page(self, soup)
        while next_page:
            page = requests.get(urljoin(BASE_URL, next_page["href"])).content
            soup = BeautifulSoup(page, "html.parser")
            quotes.extend(self.get_product_on_page(self, soup))
            next_page = self.get_next_page(self, soup)

        return quotes

    def get_next_page(self, page_soup: BeautifulSoup) -> str | None:
        return page_soup.select_one("li.next > a")


def write_to_csv(output_csv_path: str, quotes: Quote) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = Quote.get_quotes(Quote)
    write_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
