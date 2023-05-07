import csv
from dataclasses import dataclass, astuple, fields
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup):
    return Quote(
        text=quote_soup.select_one(".text").text.replace("”", ""),
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def parse_single_page(page_soup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def write_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(FIELDS)
        writer.writerows((astuple(quote) for quote in quotes))


def get_soup(url):
    response = requests.get(url).content
    return BeautifulSoup(response, "html.parser")


def main(output_csv_path: str) -> None:
    soup = get_soup(BASE_URL)
    all_quotes = parse_single_page(soup)
    next_page = soup.select(".next > a[href]")
    while next_page:
        next_page_url = urljoin(BASE_URL, next_page[0]["href"])
        soup = get_soup(next_page_url)
        all_quotes.extend(parse_single_page(soup))
        next_page = soup.select(".next > a[href]")
    write_to_csv(all_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
