import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup

HOME_URL = "https://quotes.toscrape.com/"
QUOTES_OUTPUT_CSV_PATH = "result.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    @classmethod
    def parse_single_quote(cls, quote_soup: BeautifulSoup) -> "Quote":
        return cls(
            text=quote_soup.select_one(".text").text,
            author=quote_soup.select_one(".author").text,
            tags=list(element.text for element in quote_soup.select(".tag"))
        )


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [Quote.parse_single_quote(quote_soup) for quote_soup in quotes]


def get_home_quote() -> [Quote]:
    page = requests.get(HOME_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(first_page_soup)
    current_page = 2

    while True:
        page = requests.get(HOME_URL + f"page/{current_page}/").content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))

        current_page += 1
        if not soup.select("li.next"):
            break

    return all_quotes


def with_products_to_csv(quotes: [Quote]) -> None:
    with open(
            QUOTES_OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_home_quote()
    with_products_to_csv(quotes)


if __name__ == "__main__":
    main("quotes.csv")
