import csv
from dataclasses import dataclass, fields, astuple

from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def quote_filler(soup: BeautifulSoup) -> list[Quote]:
    quotes = soup.find_all("div", {"class": "quote"})
    lst = []
    for quote in quotes:
        lst.append(
            Quote(
                str(quote.select_one(".text").text),
                str(quote.select_one(".author").text),
                [tag.text for tag in quote.select(".tag")]
            )
        )
    return lst


def csv_creator(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    url = BASE_URL
    all_quotes = []
    while True:
        text = requests.get(url)
        soup = BeautifulSoup(text.content, "html.parser")
        all_quotes.extend(quote_filler(soup))
        next_page = soup.select_one("li.next a")
        if not next_page:
            break
        url = urljoin(BASE_URL, next_page["href"])
    csv_creator(all_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
