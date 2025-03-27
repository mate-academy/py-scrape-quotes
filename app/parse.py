import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import Tag, BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"

@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return (Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select_one(".tags").select(".tag")]
    ))


def get_single_page_quotes(page_soup: Tag) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_page_quotes() -> [Quote]:
    text = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(text, "html.parser")

    all_quotes = get_single_page_quotes(first_page_soup)

    for page_num in range(2, 11):
        text = requests.get(BASE_URL + f"page/{page_num}/").content
        next_page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(next_page_soup))

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_page_quotes()
    with open(output_csv_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])

if __name__ == "__main__":
    main("quotes.csv")
