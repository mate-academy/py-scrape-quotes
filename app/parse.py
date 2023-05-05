from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag

import requests as requests
import csv


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELD = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags > a.tag")]
    )


def parse_quotes(url: str, list_of_quotes: list) -> list[Quote]:
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    quotes = soup.select(".quote")

    for quote in quotes:
        list_of_quotes.append(parse_single_quote(quote))
    next_page = soup.select_one(".pager > .next > a")

    if next_page:
        next_page = next_page["href"]
        parse_quotes(urljoin(BASE_URL, next_page), list_of_quotes)

    return list_of_quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELD)
        quotes = parse_quotes(BASE_URL, [])
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
