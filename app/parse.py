import csv
from dataclasses import dataclass, fields, astuple
from bs4 import Tag, BeautifulSoup
import requests

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_single_page_quotes(page_soup: Tag) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quotes(first_page_soup)

    for page in range(2, 11):
        page = requests.get("".join((BASE_URL, f"page/{1 + 2}/"))).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    print(quotes)
    with open(output_csv_path, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
