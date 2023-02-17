import csv
import time
from concurrent.futures import ProcessPoolExecutor, wait

import requests
import threading
import multiprocessing

from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    biography: str


BASE_URL = "https://quotes.toscrape.com"
global_quotes = []
global_authors = []
authors_page_soup = set()


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]


def parse_single_quote(page_soup: BeautifulSoup) -> None:
    global_quotes.append(Quote(
        text=page_soup.select_one(".text").text,
        author=page_soup.select_one(".author").text,
        tags=[tag.text for tag in page_soup.select(".tag")]
    ))


def parse_single_author(page_soup: BeautifulSoup) -> None:
    global_authors.append(Author(
        biography=page_soup.select_one(
            ".author-details"
        ).text.replace("\n", " "),
    ))


def write_list_in_file(
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


def get_author_soup(author_url: BeautifulSoup) -> None:
    url = urljoin(
        BASE_URL,
        author_url.select_one("a").get("href")
    )
    page = requests.get(url).content
    authors_page_soup.add(BeautifulSoup(page, "html.parser"))


def get_all_page_soup() -> list[BeautifulSoup]:
    all_page_soup = []

    page = requests.get(BASE_URL).content
    page_soup = BeautifulSoup(page, "html.parser")
    all_page_soup.append(page_soup.select(".quote"))

    while page_soup.find("li", class_="next"):
        pagination = page_soup.select_one(".next > a").get("href")
        next_url = urljoin(BASE_URL, pagination)
        page = requests.get(next_url).content
        page_soup = BeautifulSoup(page, "html.parser")
        all_page_soup.append(page_soup.select(".quote"))
    return all_page_soup


def main(output_csv_path: str) -> None:
    page_soup = get_all_page_soup()

    tasks = []
    for page in page_soup:
        for quote in page:
            tasks.append(threading.Thread(
                target=parse_single_quote,
                args=(quote,))
            )
            tasks[-1].start()

        for author_url in page:
            tasks.append(threading.Thread(
                target=get_author_soup,
                args=(author_url,))
            )
            tasks[-1].start()
    for task in tasks:
        task.join()

    tasks = []
    for authors in authors_page_soup:
        tasks.append(threading.Thread(
            target=parse_single_author,
            args=(authors,))
        )
        tasks[-1].start()
    for task in tasks:
        task.join()

    with ProcessPoolExecutor(multiprocessing.cpu_count() - 1) as executor:
        futures = [executor.submit(write_list_in_file,
                                   output_csv_path,
                                   global_quotes,
                                   QUOTE_FIELDS),
                   executor.submit(write_list_in_file,
                                   "authors.csv",
                                   global_authors,
                                   AUTHOR_FIELDS)]
    wait(futures)


if __name__ == "__main__":
    star = time.perf_counter()
    main("quotes.csv")
    print(f"Elapsed: {time.perf_counter() - star}")
