import csv
import requests

from dataclasses import dataclass
from bs4 import BeautifulSoup

BASE_URL = "http://quotes.toscrape.com"
PAGES_URL = "https://quotes.toscrape.com/page/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_quotes() -> tuple[list[Quote], dict]:
    quotes_list = []
    biography_link = {}

    page_num = 1
    quotes = BeautifulSoup(
        requests.get(f"{PAGES_URL}{page_num}/").content,
        "html.parser"
    ).select(".quote")

    while quotes:
        for quote in quotes:
            quotes_list.append(Quote(
                text=quote.select_one(".text").text,
                author=quote.select_one(".author").text,
                tags=[tag.text for tag in quote.select(".tag")]
            ))

            author_link = quote.find("a", href=True)
            biography_link[quote.select_one(
                ".author").text] = (BASE_URL + author_link["href"])

        page_num += 1
        quotes = BeautifulSoup(
            requests.get(f"{PAGES_URL}{page_num}/").content,
            "html.parser"
        ).select(".quote")

    return quotes_list, biography_link


def main(output_csv_path: str, links_csv_path: str) -> None:

    with (open(output_csv_path, "w", newline="") as csv_quotes,
          open(links_csv_path, "w", newline="") as csv_links):
        headers = ["text", "author", "tags"]
        writer = csv.writer(csv_quotes, delimiter=";")
        writer.writerow(headers)

        for quote in get_quotes()[0]:
            writer.writerow(
                [quote.text.replace("“", '"').replace("”", '"')
                 .replace("′", "'"), quote.author, quote.tags]
            )

        headers = ["author", "link"]
        writer = csv.writer(csv_links, delimiter=";")
        writer.writerow(headers)

        for author, link in get_quotes()[1].items():
            writer.writerow([author, link])


if __name__ == "__main__":
    main("quotes.csv", "links.csv")
