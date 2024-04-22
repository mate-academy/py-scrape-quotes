import csv
import requests

from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag

URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(product_soup: Tag) -> Quote:
    tag_elements = product_soup.select(".tags .tag")
    tags = [tag.text for tag in tag_elements]
    return Quote(
        text=product_soup.select_one(".text").text,
        author=product_soup.select_one(".author").text,
        tags=tags
    )


def get_all_quotes() -> list:
    quotes = []
    page_num = 1

    while True:
        curr_url = urljoin(URL, f"/page/{page_num}/")
        page = requests.get(curr_url).content
        soup = BeautifulSoup(page, "html.parser")
        page_quotes = soup.select(".quote")
        quotes.extend([parse_single_quote(quote) for quote in page_quotes])
        if not soup.select("li.next"):
            break
        page_num += 1

    return quotes


def write_quotes_to_csv(quotes: list, output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("results.csv")
