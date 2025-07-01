import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

URL_NAME = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

QUOTE_ROWS = [i.name for i in fields(Quote)]

def get_text(soup):
    quotes = []

    for quote in soup:
        text = quote.select_one(".text").get_text()
        author = quote.select_one(".author").get_text()
        tags = [t.get_text() for t in quote.select(".tag")]

        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def get_url_with_pagination(page_num):
    path = urljoin(URL_NAME, f"/page/{page_num}")
    print(path)
    return path


def write_data_to_csv(filename: str, data_to_write: list[Quote]):
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_ROWS)
        writer.writerows([astuple(data) for data in data_to_write])


def parse_web_site(filename: str):
    status = True
    last_num = 1
    list_of_data = []

    while status is True:
        text = requests.get(get_url_with_pagination(last_num)).content
        soup = BeautifulSoup(text, "html.parser")
        data_scraped = soup.select(".quote")

        if data_scraped:
            text_scraped = get_text(data_scraped)
            list_of_data.extend(text_scraped)
            last_num += 1
        else:
            status = False

    write_data_to_csv(filename, list_of_data)


def main(output_csv_path: str) -> None:
    parse_web_site(output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
