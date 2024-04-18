import re
from typing import List

import requests
from bs4 import BeautifulSoup, Tag

from app.models import Quote
from app.writer import write_quotes_to_csv


BASE_URL = "https://quotes.toscrape.com/"


def get_single_quote(tag: Tag) -> Quote:
    text = tag.select_one("span.text").text
    author = tag.select_one("small.author").text
    tags = [tag.text for tag in tag.select("a.tag")]

    return Quote(text=text, author=author, tags=tags)


def get_page_soup(page_number: int) -> BeautifulSoup:
    request_url = BASE_URL + "page/" + str(page_number) + "/"

    page = requests.get(request_url).content
    soup = BeautifulSoup(page, "html.parser")

    return soup


def get_quotes() -> List[Quote]:
    page_number = 1
    quotes = []

    while True:
        soup = get_page_soup(page_number)
        pagination = soup.select_one("li.next a")

        html_blocks = soup.select("div.quote")

        quotes += [get_single_quote(block) for block in html_blocks]

        if pagination is None:
            break

        pagination = pagination["href"]
        page_number = re.search(r"\d+", pagination).group()

    return quotes


def main(output_csv_path: str) -> None:
    quotes_obj_list = get_quotes()
    write_quotes_to_csv(output_csv_path, quotes_obj_list)


if __name__ == "__main__":
    main("result.csv")
