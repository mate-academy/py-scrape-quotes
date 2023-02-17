import csv
import time
import requests
import threading
import multiprocessing

from dataclasses import fields, astuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from parse import Quote, Author


class ParseQuote:
    _base_url = "https://quotes.toscrape.com"
    _quote_fields = [field.name for field in fields(Quote)]
    _authors_fields = [field.name for field in fields(Author)]
    _quotes = []
    _authors = []
    _authors_page_soup = set()

    def _parse_single_quote(self, page_soup: BeautifulSoup) -> None:
        self._quotes.append(Quote(
            text=page_soup.select_one(".text").text,
            author=page_soup.select_one(".author").text,
            tags=[tag.text for tag in page_soup.select(".tag")]
        ))

    def _parse_single_author(self, page_soup: BeautifulSoup) -> None:
        self._authors.append(Author(
            biography=page_soup.select_one(
                ".author-details"
            ).text.replace("\n", " "),
        ))

    @staticmethod
    def _write_list_in_file(
            output_csv_path: str,
            name_file: list,
            field: list[fields],
    ) -> None:
        with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(field)
            writer.writerows(
                [astuple(dataclass_inst) for dataclass_inst in name_file]
            )

    def _get_author_soup(self, author_url: BeautifulSoup) -> None:
        url = urljoin(
            self._base_url,
            author_url.select_one("a").get("href")
        )
        page = requests.get(url).content
        self._authors_page_soup.add(BeautifulSoup(page, "html.parser"))

    def _get_authors_page_soup(self, page_soup: list[BeautifulSoup]) -> None:
        tasks = []
        for author_url in page_soup:
            tasks.append(threading.Thread(
                target=self._get_author_soup, args=(author_url,))
            )
            tasks[-1].start()
        for task in tasks:
            task.join()

    def _get_all_page_soup(self) -> list[BeautifulSoup]:
        all_page_soup = []

        page = requests.get(self._base_url).content
        page_soup = BeautifulSoup(page, "html.parser")
        all_page_soup.append(page_soup.select(".quote"))

        while page_soup.find("li", class_="next"):
            pagination = page_soup.select_one(".next > a").get("href")
            next_url = urljoin(self._base_url, pagination)
            page = requests.get(next_url).content
            page_soup = BeautifulSoup(page, "html.parser")
            all_page_soup.append(page_soup.select(".quote"))
        return all_page_soup

    def main(self) -> None:
        page_soup = self._get_all_page_soup()

        tasks = []
        for page in page_soup:
            tasks.append(threading.Thread(
                target=self._get_authors_page_soup,
                args=(page,))
            )
            tasks[-1].start()
            for quote in page:
                tasks.append(threading.Thread(
                    target=self._parse_single_quote,
                    args=(quote,))
                )
                tasks[-1].start()
        for task in tasks:
            task.join()

        tasks = []
        for authors in self._authors_page_soup:
            tasks.append(threading.Thread(
                target=self._parse_single_author,
                args=(authors,))
            )
            tasks[-1].start()
        for task in tasks:
            task.join()

        tasks = [multiprocessing.Process(
            target=self._write_list_in_file,
            args=("quotes.csv", self._quotes, self._quote_fields))
        ]
        tasks[-1].start()
        tasks.append(multiprocessing.Process(
            target=self._write_list_in_file,
            args=("authors.csv", self._authors, self._authors_fields))
        )
        tasks[-1].start()
        for task in tasks:
            task.join()


if __name__ == "__main__":
    star = time.perf_counter()
    parser = ParseQuote()
    parser.main()
    print(f"Elapsed: {time.perf_counter() - star}")
