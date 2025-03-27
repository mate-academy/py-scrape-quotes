from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup, ResultSet
import requests
import csv


HOME_URL = "https://quotes.toscrape.com/page/{page_number}/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_quotes_data(quotes: ResultSet) -> list[Quote]:
    quotes_inform = [
        Quote(
            text=quote.select_one(".text").text,
            author=quote.select_one("small.author").text,
            tags=[
                tag.get_text()
                for tag in quote.find_all("a", attrs={"class": "tag"})
            ],
        )
        for quote in quotes
    ]
    return quotes_inform


def get_quotes_from_pages() -> list[Quote]:
    counter = 1
    all_quotes_from_page = []

    while True:
        page = requests.get(HOME_URL.format(page_number=counter))
        soup = BeautifulSoup(page.content, "html.parser")

        quotes = soup.find_all("div", attrs={"class": "quote"})
        all_quotes_from_page.extend(get_quotes_data(quotes))
        counter += 1

        if page.status_code != 200 or not soup.select("nav ul li.next"):
            return all_quotes_from_page


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(
            [
                astuple(quote)
                for quote in get_quotes_from_pages()
            ]
        )


if __name__ == "__main__":
    main("quotes.csv")
