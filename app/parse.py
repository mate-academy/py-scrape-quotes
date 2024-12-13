import csv
from dataclasses import dataclass, astuple, fields
import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"
QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one("span.text").text,
        author=quote.select_one("small.author").text,
        tags=[tag.text for tag in quote.select_one(".tags").findAll(
            "a", class_="tag"
        )],
    )


def get_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_quote(quote) for quote in quotes]


def get_current_page(url: str) -> BeautifulSoup:
    response = requests.get(url).content
    return BeautifulSoup(response, "html.parser")


def get_quotes() -> [Quote]:
    current_page = get_current_page(BASE_URL)
    all_quotes = get_page_quotes(current_page)
    current_page_num = 1
    while current_page.select("li.next a"):
        current_page_num += 1
        next_url = f"{BASE_URL}page/{current_page_num}/"
        current_page = get_current_page(next_url)
        quotes = get_page_quotes(current_page)
        all_quotes.extend((quote for quote in quotes))
    return all_quotes


def write_quotes_to_csv(quotes: list, output_csv_path: str) -> None:
    with open("result.csv", "w", encoding="UTF-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
