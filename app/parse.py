import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup):
    single_quote = (dict(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]

    ))
    return Quote(
        text=single_quote["text"],
        author=single_quote["author"],
        tags=single_quote["tags"],
    )


def get_num_pages():
    url = "http://quotes.toscrape.com/page/1/"
    count = 1

    while True:
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        next_page_element = soup.select_one("li.next > a")

        if next_page_element:
            count += 1
            next_page_url = next_page_element.get("href")
            url = urljoin(url, next_page_url)
        else:
            break

    return count


def get_single_page_quotes(page_soup):
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes():
    all_quotes = []
    num_pages = get_num_pages()

    for page_num in range(1, num_pages + 1):
        url = urljoin(URL, ("page/" + str(page_num)))
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
