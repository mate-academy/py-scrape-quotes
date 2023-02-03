import collections
import csv
from dataclasses import dataclass, fields
from urllib.parse import urljoin

import requests
from bs4 import Tag, BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_absolute_url(base_url: str, relative_url: str) -> str:
    return urljoin(base_url, relative_url)


def get_page_soup(url: str) -> BeautifulSoup:
    web_page = requests.get(url).content
    return BeautifulSoup(web_page, "html.parser")


def get_single_quotes(quote_tag: Tag) -> Quote:
    return Quote(
        text=quote_tag.select_one(".text").string,
        author=quote_tag.select_one(".author").string,
        tags=[
            tag.string
            for tag in quote_tag.select(".tag")
        ]
    )


def parse_quotes_on_the_page(page_soup: BeautifulSoup) -> list[Quote]:
    return [
        get_single_quotes(quote)
        for quote in page_soup.select(".quote")
    ]


def get_next_quotes_from_pages(
        current_page_soup: BeautifulSoup,
        base_url: str
) -> collections:
    next_page_tag = current_page_soup.select_one(".pager > .next > a")
    while next_page_tag:
        next_page_url = get_absolute_url(base_url, next_page_tag["href"])
        page_soup = get_page_soup(next_page_url)
        yield parse_quotes_on_the_page(page_soup)

        next_page_tag = page_soup.select_one(".pager > .next > a")


def get_all_quotes(url: str) -> list[Quote]:
    page_soup = get_page_soup(url)
    quotes = parse_quotes_on_the_page(page_soup)

    for page_quotes in get_next_quotes_from_pages(page_soup, url):
        quotes.extend(page_quotes)

    return quotes


def main(output_csv_path: str) -> None:
    quote_fields = [field.name for field in fields(Quote)]
    base_url = "https://quotes.toscrape.com/"
    quotes = get_all_quotes(base_url)

    with open(output_csv_path, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(quote_fields)
        writer.writerows(
            [
                [getattr(quote, field.name) for field in fields(Quote)]
                for quote in quotes
            ]
        )


if __name__ == "__main__":
    main("quotes.csv")
