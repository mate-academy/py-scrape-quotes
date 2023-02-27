import csv
from typing import Union, List
from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup
import requests


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_page_html(url: str) -> BeautifulSoup:
    response = requests.get(url).content
    return BeautifulSoup(response, "html.parser")


def get_path_to_next_page(url: str) -> Union[str, bool]:
    link_to_next_page = get_page_html(url).select_one(
        ".pager > .next"
    )
    if link_to_next_page:
        return str(link_to_next_page.find_next("a")["href"])[1:]
    return False


def parse_single_page_quotes() -> List[Quote]:
    quotes = get_page_html(BASE_URL).select(".quote")
    quotes_text = [text.select_one(".text").text for text in quotes]
    quotes_author = [
        text.select_one(".author").text for text in quotes
    ]
    quotes_tags = [
        [tag.text for tag in text.select(".tag")] for text in quotes
    ]
    return [
        Quote(
            text=quotes_text[index],
            author=quotes_author[index],
            tags=quotes_tags[index]
        ) for index in range(len(quotes))
    ]


def get_all_quotes(url: str) -> list[Quote]:
    current_url = url

    quotes = parse_single_page_quotes(current_url)
    page = 1

    while get_path_to_next_page(current_url):
        page += 1
        quotes += parse_single_page_quotes(url + f"page/{page}/")

    return quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        quotes = get_all_quotes(BASE_URL)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


if __name__ == "__main__":
    main("quotes.csv")
