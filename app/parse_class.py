import csv
import time
import requests

from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from parse import Quote, Author


@dataclass
class ParseQuote:
    base_url = "https://quotes.toscrape.com"
    authors_url = set()
    quote_fields = [field.name for field in fields(Quote)]
    author_fields = [field.name for field in fields(Author)]

    @staticmethod
    def _parse_single_quote(page_soup: BeautifulSoup) -> Quote:
        return Quote(
            text=page_soup.select_one(".text").text,
            author=page_soup.select_one(".author").text,
            tags=[tag.text for tag in page_soup.select(".tag")]
        )

    @staticmethod
    def _parse_single_author(page_soup: BeautifulSoup) -> Author:
        return Author(
            biography=page_soup.select_one(
                ".author-details"
            ).text.replace("\n", " "),
        )

    @staticmethod
    def _write_list_in_file(
            output_csv_path: str,
            name_file: list[object],
            fields: list[fields],
    ) -> None:
        with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(fields)
            writer.writerows([astuple(name) for name in name_file])

    def _get_authors_page_soup(
            self,
            page_soup: list[BeautifulSoup]
    ) -> list[BeautifulSoup]:
        result_authors = []
        for author_url in page_soup:
            url = urljoin(
                self.base_url,
                author_url.select_one("a").get("href")
            )
            if url not in self.authors_url:
                page = requests.get(url).content
                result_authors.append(BeautifulSoup(page, "html.parser"))
            self.authors_url.add(url)
        return result_authors

    def _get_all_page_soup(self) -> list[BeautifulSoup]:
        result_page_soup = []

        page = requests.get(self.base_url).content
        page_soup = BeautifulSoup(page, "html.parser")
        result_page_soup.append(page_soup.select(".quote"))

        while page_soup.find("li", class_="next"):
            pagination = page_soup.select_one(".next > a").get("href")
            next_url = urljoin(self.base_url, pagination)
            page = requests.get(next_url).content
            page_soup = BeautifulSoup(page, "html.parser")
            result_page_soup.append(page_soup.select(".quote"))
        return result_page_soup

    def main(self) -> None:
        result_quotes = []
        result_authors = []
        list_page_soup = self._get_all_page_soup()
        for page_soup in list_page_soup:
            authors_page_soup = self._get_authors_page_soup(page_soup)

            result_quotes.extend(
                [self._parse_single_quote(quote)
                 for quote in page_soup]
            )
            result_authors.extend(
                [self._parse_single_author(author)
                 for author in authors_page_soup]
            )

        self._write_list_in_file(
            "quotes.csv",
            result_quotes,
            self.quote_fields
        )
        self._write_list_in_file(
            "authors.csv",
            result_authors,
            self.author_fields
        )


if __name__ == "__main__":
    star = time.perf_counter()

    quotes = ParseQuote()
    quotes.main()

    print(f"Elapsed: {time.perf_counter() - star}")
