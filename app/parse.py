import csv
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, SoupStrainer


BASE_URL = "https://quotes.toscrape.com/"
NEXT_PAGE_URL = "page/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_element: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_element.select_one(".text").text,
        author=quote_element.select_one(".author").text,
        tags=[tag.text for tag in quote_element.select(".tag")],
    )


def filter_for_quotes_elements(tag: str, tag_args_dict: dict) -> bool:
    return tag == "div" and "quote" == tag_args_dict.get("class")


quotes_strainer = SoupStrainer(filter_for_quotes_elements)
pagination_strainer = SoupStrainer("ul", class_="pager")


def get_all_page_quotes(page: str) -> list[Quote]:
    soup = BeautifulSoup(page, "html.parser", parse_only=quotes_strainer)
    quotes_elements = soup.select(".quote")
    quotes_instances = [parse_single_quote(quote) for quote in quotes_elements]
    return quotes_instances


def get_all_quotes_instances(base_url: str = BASE_URL) -> list[Quote]:
    page_count = 1
    quotes_list = []
    while True:
        page_link = urljoin(base_url, f"{NEXT_PAGE_URL}{page_count}/")
        page = requests.get(page_link).content
        current_page_soup = BeautifulSoup(
            page, "html.parser", parse_only=pagination_strainer
        )

        current_page_quotes = get_all_page_quotes(page)
        quotes_list.extend(current_page_quotes)

        if current_page_soup.select_one("li.next"):
            page_count += 1
        else:
            break

    return quotes_list


def main(output_csv_path: str) -> None:
    print("writing quotes to csv...")
    quotes_list = get_all_quotes_instances()
    with open(output_csv_path, "w", newline="") as csv_file:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for quote in quotes_list:
            writer.writerow(
                {
                    "text": quote.text,
                    "author": quote.author,
                    "tags": quote.tags,
                }
            )


if __name__ == "__main__":
    main("quotes.csv")
    get_all_quotes_instances()
