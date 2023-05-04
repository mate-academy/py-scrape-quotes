import csv
import requests

from dataclasses import dataclass
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes_list = []
    quotes = page_soup.select(".quote")

    for quote in quotes:
        quotes_list.append(Quote(
            text=quote.select_one(".text").text,
            author=quote.select_one(".author").text,
            tags=[tag.text for tag in quote.select(".tag")]
        ))

    return quotes_list


def get_quotes() -> list[Quote]:
    all_quotes_list = []

    with requests.Session() as session:
        url = BASE_URL
        url_list = [url]

        while True:
            response = session.get(url)
            page_soup = BeautifulSoup(response.content, "html.parser")
            all_quotes_list.extend(get_single_page_quotes(page_soup))
            next_page = page_soup.select_one(".next > a")
            url_list.append(next_page)
            try:
                url = f"{BASE_URL}{next_page['href']}"
            except TypeError:
                break

    return all_quotes_list


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="") as csv_quotes:
        headers = ["text", "author", "tags"]
        writer = csv.writer(csv_quotes)
        writer.writerow(headers)
        for quote in get_quotes():
            writer.writerow(
                [quote.text, quote.author, quote.tags]
            )


if __name__ == "__main__":
    main("quotes.csv")
