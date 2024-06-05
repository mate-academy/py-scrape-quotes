import csv
from dataclasses import dataclass, fields
from typing import List
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").get_text(strip=True)
    author = quote_soup.select_one(".author").get_text(strip=True)
    tag_elements = quote_soup.select(".tag")
    tags = [tag_element.get_text(strip=True) for tag_element in tag_elements]
    return Quote(text, author, tags)


def get_quotes_from_page(page_url: str) -> List[Quote]:
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    quote_elements = soup.select(".quote")
    quotes = [parse_single_quote(quote_element)
              for quote_element in quote_elements]
    next_page = soup.select_one(".next > a")
    if next_page is not None:
        quotes.extend(
            get_quotes_from_page(
                "https://quotes.toscrape.com" + next_page["href"]
            )
        )
    return quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes_from_page(BASE_URL)
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [field.name for field in fields(Quote)]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([quote.__dict__ for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
