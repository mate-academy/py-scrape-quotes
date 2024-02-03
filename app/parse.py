import csv
from dataclasses import dataclass, fields, astuple
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    born_date: datetime
    born_location: str
    description: str


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


class QuotesScraper:
    BASE_URL = "https://quotes.toscrape.com/"
    AUTHORS_OUTPUT_CSV_PATH = "authors.csv"

    def __init__(self) -> None:
        self.AUTHORS = {}

    def parse_single_author(self, soup: BeautifulSoup) -> Author:
        author_url = urljoin(self.BASE_URL, soup.select_one("a")["href"])
        author_page = requests.get(author_url).content
        soup = BeautifulSoup(author_page, "html.parser")

        return Author(
            name=soup.select_one(".author-title").text,
            born_date=datetime.strptime(
                soup.select_one(".author-born-date").text, "%B %d, %Y"
            ),
            born_location=soup.select_one(".author-born-location").text[3:],
            description=soup.select_one(".author-description").text.strip()
        )

    def parse_single_quote_and_author(self, soup: BeautifulSoup) -> Quote:
        tags = soup.select_one(".keywords")["content"].split(",")
        quote = Quote(
            text=soup.select_one(".text").text,
            author=soup.select_one(".author").text,
            tags=tags if tags != [""] else []
        )

        if quote.author not in self.AUTHORS:
            author = self.parse_single_author(soup)
            self.AUTHORS[quote.author] = author

        return quote

    def get_quotes_and_authors_from_single_page(
            self, soup: BeautifulSoup
    ) -> [Quote]:
        quotes_data = soup.select(".quote")
        return [
            self.parse_single_quote_and_author(quotes_soup)
            for quotes_soup in quotes_data
        ]

    def get_all_quotes_and_authors(self) -> [Quote]:
        session = requests.Session()
        all_quotes = []
        next_page_url = urljoin(self.BASE_URL, "")

        while True:
            page_content = session.get(next_page_url).content
            soup = BeautifulSoup(page_content, "html.parser")

            new_quotes = self.get_quotes_and_authors_from_single_page(soup)
            all_quotes.extend(new_quotes)

            try:
                next_button = soup.select_one("li.next > a")["href"]
                next_page_url = urljoin(self.BASE_URL, next_button)

            except TypeError:
                return all_quotes

    @staticmethod
    def write_data_to_csv(
            data: [Quote | Author],
            output_csv_path: str,
            col_names: list
    ) -> None:
        with open(output_csv_path, "w") as file:
            writer = csv.writer(file)
            writer.writerow(col_names)
            writer.writerows([astuple(item) for item in data])


def main(output_csv_path: str) -> None:
    scraper = QuotesScraper()
    quotes = scraper.get_all_quotes_and_authors()
    authors = scraper.AUTHORS.values()
    scraper.write_data_to_csv(quotes, output_csv_path, QUOTE_FIELDS)
    scraper.write_data_to_csv(
        authors, scraper.AUTHORS_OUTPUT_CSV_PATH, AUTHOR_FIELDS
    )


if __name__ == "__main__":
    main("quotes.csv")
