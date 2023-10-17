from dataclasses import dataclass, fields, astuple
from typing import Union
import csv

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


class QuoteParser:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    @staticmethod
    def get_page_html(url: str) -> BeautifulSoup:
        response = requests.get(url)
        response.encoding = "utf-8"
        try:
            return BeautifulSoup(response.text, "html.parser")
        except UnicodeDecodeError:
            print("Error parsing the following content from URL:", url)
            print(response.text)
            raise

    def get_path_to_next_page(self, url: str) -> Union[str, bool]:
        link_to_next_page = (
            QuoteParser.get_page_html(url).select_one(".pager > .next"))
        if link_to_next_page:
            return str(link_to_next_page.find_next("a")["href"])[1:]
        return False

    def get_quote_from_single_page(self, url: str) -> list[Quote]:
        quotes_div = QuoteParser.get_page_html(url).select(".quote")
        quotes_text = \
            [text.select_one(".text").text for text in quotes_div]
        quotes_author = \
            [text.select_one(".author").text for text in quotes_div]
        quotes_tags = \
            [[tag.text for tag in text.select(".tag")] for text in quotes_div]
        return [
            Quote(text=quotes_text[index],
                  author=quotes_author[index],
                  tags=quotes_tags[index])
            for index in range(len(quotes_div))
        ]

    def get_all_quotes(self) -> list[Quote]:
        current_url = self.base_url
        quotes = self.get_quote_from_single_page(current_url)
        page = 1
        while self.get_path_to_next_page(current_url):
            page += 1
            current_url = self.base_url + f"page/{page}/"
            quotes += self.get_quote_from_single_page(current_url)
        return quotes


def main(output_csv_path: str) -> None:
    parser = QuoteParser(BASE_URL)
    quotes = parser.get_all_quotes()
    with open(output_csv_path, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


if __name__ == "__main__":
    main("quotes.csv")
