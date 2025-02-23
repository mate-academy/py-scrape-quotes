import csv
import requests

from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass, fields, astuple



BASE_URL = "https://quotes.toscrape.com"

@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

QUOTE_FIELDS = [field.name for field in fields(Quote)]

def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_single_page_quotes(page_soup: Tag):
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_pages_quotes() -> [Quote]:
    quotes = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(quotes, "html.parser")

    all_quotes = get_single_page_quotes(first_page_soup)
    page_num = 2

    while True:
        url = requests.get(BASE_URL, params={"page": page_num})
        response = requests.get(url)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        next_button = soup.select_one(".pager .next a")

        if not next_button:
            break
        next_page = BeautifulSoup(url, "html.parser")
        all_quotes.extend(get_single_page_quotes(next_page))
        page_num += 1

    return all_quotes

def write_to_csv(quotes: [Quote], output_csv_path) -> None:
    with open(output_csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])

def main(output_csv_path: str) -> None:
    quotes = get_all_pages_quotes()
    write_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
