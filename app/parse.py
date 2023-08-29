import csv
from dataclasses import dataclass, fields, astuple
from requests import request
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_page(base_url: str, page_num: int) -> BeautifulSoup:
    url = BASE_URL + f"/page/{page_num}/"
    page = request("get", url).content
    soup = BeautifulSoup(page, "html.parser")
    return soup


def get_quotes_soup(soup: BeautifulSoup) -> list:
    quotes = soup.select("div.quote")
    return quotes


def parse_quote(quote_soup: BeautifulSoup) -> Quote:
    quote = Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
        )
    return quote


def get_all_quotes() -> list[Quote]:
    all_qoutes = []
    next_page = 1
    while next_page:
        page = get_page(BASE_URL, next_page)
        qoutes_soup = get_quotes_soup(page)
        quotes = [parse_quote(quote) for quote in qoutes_soup]
        all_qoutes.extend(quotes)
        next_page += 1
        if not page.select(".next"):
            next_page = None
    return all_qoutes


def write_quotes(quotes_list: [Quote], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8", newline="") as quotes_file:
        writer = csv.DictWriter(quotes_file, QUOTE_FIELDS)
        writer.writeheader()
        for quote in quotes_list:
            writer.writerow({
                "text": quote.text,
                "author": quote.author,
                "tags": quote.tags
            })


def main(output_csv_path: str) -> None:
    quotes_list = get_all_quotes()
    write_quotes(quotes_list, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
