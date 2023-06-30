from dataclasses import dataclass, astuple
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

QUOTES_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def write_quotes_to_csv(output_csv_path: str, quotes: Quote) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        header = ["text", "author", "tags"]
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows([astuple(quote) for quote in quotes])


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags > a.tag")]
    )


def parse_quotes_from_page(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_next_page(page_soup: BeautifulSoup) -> str | None:
    return page_soup.select_one("li.next > a")


def get_quotes(quotes_url: str) -> [Quote]:
    page = requests.get(quotes_url).content
    soup = BeautifulSoup(page, "html.parser")
    next_page = get_next_page(soup)
    quotes = parse_quotes_from_page(soup)
    while next_page:
        page = requests.get(urljoin(quotes_url, next_page["href"])).content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(parse_quotes_from_page(soup))
        next_page = get_next_page(soup)

    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes(QUOTES_URL)
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
