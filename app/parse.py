import csv
import logging
import sys
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, Tag

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    born: str
    description: str


class QuoteAuthorScraper:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.cached_author_hrefs: [str] = []

    @staticmethod
    def get_page_soup(url: str) -> BeautifulSoup:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, features="html.parser")

    @staticmethod
    def parse_single_quote(quote_soup: Tag) -> Quote:
        return Quote(
            text=quote_soup.select_one(".text").text,
            author=quote_soup.select_one(".author").text,
            tags=[tag.get_text() for tag in quote_soup.select(".tag")],
        )

    @staticmethod
    def prettify_description(text: str) -> str:
        """Mainly to remove unexpected whitespace characters"""
        return " ".join(text.split()).replace("''", '"')

    def parse_single_author(self, author_href: str) -> Author:
        author_page_soup = self.get_page_soup(self.base_url + author_href)

        author = Author(
            name=author_page_soup.select_one(".author-title").text,
            born=author_page_soup.select_one(".author-born-date").text
            + " "
            + author_page_soup.select_one(".author-born-location").text,
            description=self.prettify_description(
                author_page_soup.select_one(".author-description").text
            ),
        )

        logging.info(f"Adding author: {author}")

        return author

    def get_single_page_quotes(self, page_soup: BeautifulSoup) -> [Quote]:
        quotes = page_soup.select(".quote")

        return [self.parse_single_quote(quote) for quote in quotes]

    def get_single_page_authors(self, page_soup: BeautifulSoup) -> [Author]:
        authors_soup = page_soup.select("a[href^='/author/']")
        authors = []

        for author in authors_soup:
            author_href = author.get("href")
            if author_href not in self.cached_author_hrefs:
                authors.append(self.parse_single_author(author_href))
                self.cached_author_hrefs.append(author_href)
            else:
                logging.info(
                    f'Author already added ({author_href.split("/")[-1]})'
                )

        return authors

    def get_authors_and_quotes(self) -> ([Author], [Quote]):
        """Authors and quotes scraping done in a single cycle for minimizing
        the number of requests"""
        first_page_soup = self.get_page_soup(self.base_url)
        all_authors = self.get_single_page_authors(first_page_soup)
        all_quotes = self.get_single_page_quotes(first_page_soup)

        next_page = first_page_soup.select_one(".next > a")

        while next_page:
            logging.info(
                "Starting scraping page #"
                f'{next_page.get("href").split("/")[2]}'
            )

            page_soup = self.get_page_soup(
                self.base_url + next_page.get("href")
            )
            all_authors.extend(self.get_single_page_authors(page_soup))
            all_quotes.extend(self.get_single_page_quotes(page_soup))

            next_page = page_soup.select_one(".next > a")

        return all_authors, all_quotes

    @staticmethod
    def save_to_csv(
        authors: [Author], quotes: [Quote], output_csv_path: str
    ) -> None:
        with open(
            output_csv_path, "w", newline="", encoding="utf-8"
        ) as quotes_file, open(
            f"authors_of_{output_csv_path}", "w", newline="", encoding="utf-8"
        ) as authors_file:
            quotes_writer = csv.writer(quotes_file)
            quotes_headers = ["text", "author", "tags"]
            quotes_writer.writerow(quotes_headers)
            for quote in quotes:
                quotes_writer.writerow([quote.text, quote.author, quote.tags])

            authors_writer = csv.writer(authors_file)
            authors_headers = ["name", "born", "description"]
            authors_writer.writerow(authors_headers)
            for author in authors:
                authors_writer.writerow(
                    [author.name, author.born, author.description]
                )


def main(output_csv_path: str) -> None:
    scraper = QuoteAuthorScraper(BASE_URL)
    authors, quotes = scraper.get_authors_and_quotes()
    scraper.save_to_csv(authors, quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
