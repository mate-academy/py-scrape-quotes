from dataclasses import dataclass, fields, astuple
import csv
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = [tag.text for tag in quote_soup.select(".tags .tag")]

    return Quote(text=text, author=author, tags=tags)


def get_quotes(url: str) -> [Quote]:
    quotes = []
    while url:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        quotes.extend(
            [parse_single_quote(quote) for quote in soup.select(".quote")]
        )
        next_page = soup.select_one(".pager .next a")
        url = urljoin(BASE_URL, next_page["href"]) if next_page else None

    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes(BASE_URL)

    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
