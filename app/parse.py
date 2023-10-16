import csv
from dataclasses import dataclass, fields, astuple
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]
    biography: str


BASE_URL = "https://quotes.toscrape.com"
QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_BIO_CACHE = {}


def get_page_html(url: str) -> BeautifulSoup:
    response = requests.get(url).content
    return BeautifulSoup(response, "html.parser")


def get_author_bio(author_url: str) -> str:
    if author_url in AUTHOR_BIO_CACHE:
        return AUTHOR_BIO_CACHE[author_url]

    soup = get_page_html(author_url)
    bio = soup.select_one(".author-description").text.strip()
    AUTHOR_BIO_CACHE[author_url] = bio
    return bio


def get_path_to_next_page(url: str) -> Optional[str]:
    link_to_next_page = get_page_html(url).select_one(
        ".pager > .next")
    if link_to_next_page:
        print(str(link_to_next_page.find_next("a")["href"])[1:])
    return None


def get_quote_from_single_page(url: str) -> list[Quote]:
    current_url = url
    quotes_div = get_page_html(current_url).select(".quote")
    quotes_text = [text.select_one(".text").text for text in quotes_div]
    quotes_author = [
        text.select_one(".author").text for text in quotes_div
    ]
    quotes_tags = [
        [tag.text for tag in text.select(".tag")] for text in quotes_div
    ]
    quotes_bio = []
    for quote_soup in quotes_div:
        author_url = urljoin(
            BASE_URL,
            quote_soup.select_one(".author + a")["href"]
        )
        quotes_bio.append(get_author_bio(author_url))

    return [
        Quote(
            text=quotes_text[index],
            author=quotes_author[index],
            tags=quotes_tags[index],
            biography=quotes_bio[index]
        ) for index in range(len(quotes_div))
    ]


def get_all_quotes(url: str) -> list[Quote]:
    current_url = url

    quotes = get_quote_from_single_page(current_url)
    page = 1

    while get_path_to_next_page(current_url):
        page += 1
        current_url = url + f"page/{page}/"
        quotes += get_quote_from_single_page(current_url)

    return quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        quotes = get_all_quotes(BASE_URL)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


if __name__ == "__main__":
    main("quotes.csv")
