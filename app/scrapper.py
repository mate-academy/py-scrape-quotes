import csv
import requests

from dataclasses import astuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.models import QUOTE_FIELDS, Quote


BASE_URL = "https://quotes.toscrape.com/"


class QuoteScrapper:

    @staticmethod
    def write_quotes_to_csv(csv_path: str, quotes: [Quote]) -> None:
        with open(csv_path, "w", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(QUOTE_FIELDS)
            writer.writerows([astuple(quote) for quote in quotes])

    @staticmethod
    def parse_single_quote(quote_soup: Tag) -> Quote:
        return Quote(
            text=quote_soup.select_one(".text").text,
            author=quote_soup.select_one(".author").text,
            tags=[tag.text for tag in quote_soup.select(".tags > .tag")]
        )

    @staticmethod
    def is_there_next_page(soup: BeautifulSoup) -> bool:
        pagination = soup.select_one(".pager > .next > a")

        return bool(pagination)

    def get_single_page_quotes(self, page_soup: BeautifulSoup) -> list[Quote]:
        quotes = page_soup.select(".quote")

        return [self.parse_single_quote(quote_soup) for quote_soup in quotes]

    def get_all_quotes(self) -> [Quote]:
        page = requests.get(BASE_URL).content
        soup = BeautifulSoup(page, "html.parser")

        all_quotes = self.get_single_page_quotes(soup)

        page_num = 2

        while self.is_there_next_page(soup):
            page = requests.get(
                urljoin(BASE_URL, f"page/{str(page_num)}/")
            ).content
            soup = BeautifulSoup(page, "html.parser")

            all_quotes.extend(self.get_single_page_quotes(soup))

            page_num += 1

        return all_quotes
