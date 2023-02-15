import csv
import threading
import time
import requests
import multiprocessing

from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ProcessPoolExecutor, wait


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    biography: str


@dataclass
class ParseQuote:
    base_url = "https://quotes.toscrape.com"
    authors_url_set = set()
    quotes_list = []
    authors_list = []

    def _parse_single_quote(self, page_soup: BeautifulSoup) -> None:
        self.quotes_list.append(Quote(
            text=page_soup.select_one(".text").text,
            author=page_soup.select_one(".author").text,
            tags=[tag.text for tag in page_soup.select(".tag")]
        ))

    def _parse_single_author(self, page_soup: BeautifulSoup) -> None:
        self.authors_list.append(Author(
            biography=page_soup.select_one(
                ".author-details"
            ).text.replace("\n", " "),
        ))

    @staticmethod
    def _write_quotes_in_file(quotes: [Quote]) -> None:
        quote_fields = [field.name for field in fields(Quote)]
        with open("quotes.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(quote_fields)
            writer.writerows([astuple(quote) for quote in quotes])

    @staticmethod
    def _write_authors_in_file(authors: [Author]) -> None:
        author_fields = [field.name for field in fields(Author)]
        with open("authors.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(author_fields)
            writer.writerows([astuple(author) for author in authors])

    def _get_authors_page_soup(
            self,
            page_soup: list[BeautifulSoup]
    ) -> list[BeautifulSoup]:
        list_authors = []
        for author_url in page_soup:
            url = urljoin(
                self.base_url,
                author_url.select_one("a").get("href")
            )
            if url not in self.authors_url_set:
                page = requests.get(url).content
                list_authors.append(BeautifulSoup(page, "html.parser"))
            self.authors_url_set.add(url)
        return list_authors

    def _get_all_page_soup(self) -> list[BeautifulSoup]:
        list_page_soup = []

        page = requests.get(self.base_url).content
        page_soup = BeautifulSoup(page, "html.parser")
        list_page_soup.append(page_soup.select(".quote"))

        while page_soup.find("li", class_="next"):
            pagination = page_soup.select_one(".next > a").get("href")
            next_url = urljoin(self.base_url, pagination)
            page = requests.get(next_url).content
            page_soup = BeautifulSoup(page, "html.parser")
            list_page_soup.append(page_soup.select(".quote"))
        return list_page_soup

    def _get_quotes(self, list_page_soup: BeautifulSoup) -> None:
        for page_soup in list_page_soup:
            for quote in page_soup:
                self._parse_single_quote(quote)

    def _get_authors(self, list_page_soup: BeautifulSoup) -> None:
        for page_soup in list_page_soup:
            authors_page_soup = self._get_authors_page_soup(page_soup)
            for author in authors_page_soup:
                self._parse_single_author(author)

    def main(self) -> None:
        list_page_soup = self._get_all_page_soup()

        tasks = []
        with ProcessPoolExecutor(
                multiprocessing.cpu_count() - 1
        ) as executor:
            tasks.append(executor.submit(self._get_quotes, list_page_soup))
            tasks.append(executor.submit(self._get_authors, list_page_soup))
            tasks.append(
                executor.submit(self._write_quotes_in_file, self.quotes_list)
            )
            tasks.append(
                executor.submit(self._write_authors_in_file, self.authors_list)
            )
        wait(tasks)

        task1 = multiprocessing.Process(
            target=self._get_quotes, args=(list_page_soup,)
        )
        task2 = multiprocessing.Process(
            target=self._get_authors, args=(list_page_soup,)
        )
        task1.start()
        task2.start()
        task1.join()
        task2.join()

        task3 = threading.Thread(
            target=self._write_quotes_in_file, args=(self.quotes_list,)
        )
        task4 = threading.Thread(
            target=self._write_authors_in_file, args=(self.authors_list,)
        )
        task3.start()
        task4.start()
        task3.join()
        task4.join()

        # self._get_quotes(list_page_soup)
        # self._get_authors(list_page_soup)
        # self._write_quotes_in_file(self.quotes_list)
        # self._write_authors_in_file(self.authors_list)


if __name__ == "__main__":
    star = time.perf_counter()

    quotes = ParseQuote()
    quotes.main()

    print(f"Elapsed: {time.perf_counter() - star}")
