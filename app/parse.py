from dataclasses import dataclass
from typing import Union

import requests
from bs4 import BeautifulSoup
import csv


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


URL = "https://quotes.toscrape.com/"


def get_page_html(url: str) -> BeautifulSoup:
    response = requests.get(url).content
    return BeautifulSoup(response, "html.parser")


def get_path_to_next_page(url: str) -> Union[str, bool]:
    link_to_next_page = get_page_html(url).select_one(
        ".pager > .next")
    if link_to_next_page:
        return str(link_to_next_page.find_next("a")["href"])[1:]
    return False


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
    return [
        Quote(
            text=quotes_text[index],
            author=quotes_author[index],
            tags=quotes_tags[index]
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
    with open(f"{output_csv_path}", "w", encoding="utf-8", newline="") as file:
        quotes = get_all_quotes(URL)
        cursor = csv.writer(file)
        cursor.writerow(["text", "author", "tags"])
        cursor.writerows(
            [
                [
                    element.text,
                    element.author,
                    element.tags
                ]for element in quotes
            ]
        )


if __name__ == "__main__":
    main("quotes.csv")
