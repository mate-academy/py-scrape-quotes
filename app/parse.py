import dataclasses
from dataclasses import dataclass
import csv

import httpx
from bs4 import BeautifulSoup
from bs4 import Tag


ROOT_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [fild.name for fild in dataclasses.fields(Quote)]


def get_page_soup(page: int, client: httpx.Client) -> BeautifulSoup:
    response = client.get(f"{ROOT_URL}page/{page}/")
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def parse_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one("span.text").text,
        author=quote_soup.select_one("span > small.author").text,
        tags=[tag.text for tag in quote_soup.select(".tags .tag")],
    )


def parse_quotes_page(
    page_soup: BeautifulSoup,
) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_quote(quote_soup) for quote_soup in quotes]


def write_quotes_to_csv(quotes: list[Quote], file_name: str) -> None:
    with open(file_name, "w", encoding="utf-8", newline="") as file_name:
        writer = csv.writer(file_name)
        writer.writerow(QUOTE_FIELDS)
        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


def main(output_csv_path: str) -> None:
    page_number = 1
    result = []
    with httpx.Client() as client:
        while True:
            page_soup = get_page_soup(page_number, client)
            result.extend(parse_quotes_page(page_soup))
            has_next = page_soup.select_one("ul.pager > li.next")
            if not has_next:
                break
            page_number += 1
    write_quotes_to_csv(result, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
