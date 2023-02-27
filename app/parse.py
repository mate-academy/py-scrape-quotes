from typing import List, Union
import csv

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


class Quote:
    def __init__(
            self,
            text: str,
            author: str,
            tags: List[str]
    ) -> None:
        self.text = text
        self.author = author
        self.tags = tuple(tags)

    def __repr__(self) -> str:
        return f"Quote(text='{self.text}'," \
               f" author='{self.author}'," \
               f" tags={self.tags})"


def get_page_html(url: str) -> BeautifulSoup:
    response = requests.get(url).content
    return BeautifulSoup(response, "html.parser")


def get_path_to_next_page(url: str) -> Union[str, bool]:
    link_to_next_page = get_page_html(url).select_one(".pager > .next")
    if link_to_next_page:
        return link_to_next_page.find_next("a")["href"][1:]
    return False


def get_quotes_from_single_page(url: str) -> List[Quote]:
    quotes_div = get_page_html(url).select(".quote")
    return [
        Quote(
            text=text.select_one(".text").text,
            author=text.select_one(".author").text,
            tags=[tag.text for tag in text.select(".tag")],
        )
        for text in quotes_div
    ]


def get_all_quotes(url: str) -> List[Quote]:
    quotes_generator = (
        quote
        for page in range(1, float("inf"))
        if (url := url + f"page/{page}/")
        if (quotes := get_quotes_from_single_page(url))
        for quote in quotes
    )
    return list(quotes_generator)


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        quotes = get_all_quotes(BASE_URL)
        writer.writerow(("text", "author", "tags"))
        writer.writerows(
            (quote.text, quote.author, quote.tags)
            for quote in quotes
        )


if __name__ == "__main__":
    main("quotes.csv")
