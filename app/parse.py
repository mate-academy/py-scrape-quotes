import requests
import csv

from typing import Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from dataclasses import dataclass

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_simple_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[soup.text for soup in quote_soup.select(".tag")],
    )


def parse_quotes(quotes_soup: BeautifulSoup) -> list[Quote]:
    return [parse_simple_quote(quote) for quote in quotes_soup]


def get_quotes_soup(url: str) -> (BeautifulSoup, Optional[str]):
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")

    quotes = soup.select("div.quote")

    next_page = soup.select(".pager > .next > a")
    next_page_href = None

    if next_page:
        next_page_href = next_page[0]["href"]

    return quotes, next_page_href


def parse(url: str = BASE_URL) -> [Quote]:
    quotes_soup, next_page_href = get_quotes_soup(url)
    quotes_list = parse_quotes(quotes_soup)

    while next_page_href is not None:
        new_url = urljoin(BASE_URL, next_page_href)
        quotes_soup, next_page_href = get_quotes_soup(new_url)
        quotes_list.extend(parse_quotes(quotes_soup))

    return quotes_list


def write_to_csv(data: list[Quote], path_file: str) -> None:
    with open(path_file, "w", newline="", encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in data:
            tags_str = ", ".join(f"'{tag}'" for tag in quote.tags)
            writer.writerow([quote.text, quote.author, f"[{tags_str}]"])


def main(output_csv_path: str) -> None:
    quotes = parse(BASE_URL)
    write_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
