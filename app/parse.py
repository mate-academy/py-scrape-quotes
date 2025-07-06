import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


PAGE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def next_page(soup: BeautifulSoup) -> bool:
    pagination = soup.select_one("li.next")
    return pagination is not None


def make_request(url: str, page: int) -> BeautifulSoup:
    url = urljoin(url, f"page/{page}/")
    text = requests.get(url).text
    soup = BeautifulSoup(text, "html.parser")
    return soup


def get_quotes(url: str) -> list[Quote]:
    page = 1
    result = []
    while True:
        soup = make_request(url, page)
        quotes_data = soup.select("div.quote")
        for quote_data in quotes_data:
            tags_data = quote_data.select("a.tag")
            tags = [tag_data.text for tag_data in tags_data]
            result.append(
                Quote(
                    text=quote_data.select_one("span.text").text,
                    author=quote_data.select_one("small.author").text,
                    tags=tags,
                )
            )
        if not next_page(soup):
            break
        page += 1
    return result


def write_quotes_to_csv(quotes: list[Quote], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes(PAGE_URL)
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
