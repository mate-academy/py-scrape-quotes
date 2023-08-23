import csv
from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup
import requests

BASIC_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


class Parser:
    def __init__(self, basic_url: str) -> None:
        self.basic_url = basic_url

    @staticmethod
    def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
        return Quote(
            text=quote_soup.select_one(".text").text,
            author=quote_soup.select_one(".author").text,
            tags=[tag.text for tag in quote_soup.select(".tags > a")],
        )

    def parse_single_page(self, page_soup: BeautifulSoup) -> list[Quote]:
        quotes_soup = page_soup.select(".quote")
        return [self.parse_single_quote(quote) for quote in quotes_soup]

    def get_all_quotes(self) -> list[Quote]:
        page = requests.get(self.basic_url).content
        page_soup = BeautifulSoup(page, "html.parser")
        quotes = self.parse_single_page(page_soup)
        next_block = page_soup.select_one(".pager > .next")
        while next_block is not None:
            page = requests.get(
                self.basic_url + next_block.select_one("a")["href"]
            ).content
            page_soup = BeautifulSoup(page, "html.parser")
            quotes += self.parse_single_page(page_soup)
            next_block = page_soup.select_one(".pager > .next")
        return quotes

    @staticmethod
    def write_to_csv(quotes: list[Quote], file_name: str) -> None:
        with open(file_name, "w", encoding="utf-8", newline="") as quotes_file:
            writer = csv.writer(quotes_file)
            writer.writerow([field.name for field in fields(Quote)])
            writer.writerows([astuple(quote) for quote in quotes])


def main(file_name: str) -> None:
    parser = Parser(BASIC_URL)
    quotes = parser.get_all_quotes()
    parser.write_to_csv(quotes, file_name)


if __name__ == "__main__":
    main("quotes.csv")
