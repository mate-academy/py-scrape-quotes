from dataclasses import dataclass, astuple
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin

BASE_URL = "https://quotes.toscrape.com/page/1/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def write_to_csv(output_csv_path: str, quotes: Quote) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags > a.tag")]
    )


def get_product_on_page(quotes: BeautifulSoup) -> [Quote]:
    quotes = quotes.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_next_page(page_soup: BeautifulSoup) -> str | None:
    return page_soup.select_one("li.next > a")


def get_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    next_page = get_next_page(soup)
    quotes = get_product_on_page(soup)
    while next_page:
        page = requests.get(urljoin(BASE_URL, next_page["href"])).content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(get_product_on_page(soup))
        next_page = get_next_page(soup)

    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
