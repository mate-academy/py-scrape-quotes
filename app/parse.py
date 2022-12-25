import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup

URL_TO_SCRAPE = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    tags = quote.select(".tag")
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in tags]
    )


def next_page_exists(soup: BeautifulSoup) -> bool:
    next_page = soup.select_one(".next")
    return next_page is not None


def parse_all_quotes() -> list[Quote]:
    first_page = requests.get(URL_TO_SCRAPE).content
    soup = BeautifulSoup(first_page, "html.parser")
    quotes = soup.select(".quote")
    i = 2
    while next_page_exists(soup):
        page = requests.get(URL_TO_SCRAPE + f"page/{i}/").content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(soup.select(".quote"))
        i += 1
    return [parse_single_quote(quote) for quote in quotes]


def main(output_csv_path: str) -> None:
    quotes = parse_all_quotes()
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote)for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
