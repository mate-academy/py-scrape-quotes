import csv
from dataclasses import dataclass, fields
from typing import List
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"
HOME_URL = urljoin(BASE_URL, "https://quotes.toscrape.com/")
URL_PAGINATION = urljoin(BASE_URL, "https://quotes.toscrape.com/")


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


AUTHORS_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one("span.text").get_text(strip=True),
        author=quote.select_one("small.author").get_text(strip=True),
        tags=[tag.text for tag in quote.select("div.tags a.tag")],
    )


def get_quotes_from_page(url: str) -> tuple[list[Quote], str | None]:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    quotes_html = soup.select("div.quote")
    quotes = [parse_single_quote(q) for q in quotes_html]

    next_button = soup.select_one("li.next a")
    next_page = urljoin(HOME_URL, next_button["href"]) if next_button else None

    return quotes, next_page


def main(output_csv_path: str) -> None:
    all_quotes: List[Quote] = []
    current_url = BASE_URL

    while current_url:
        quotes, current_url = get_quotes_from_page(current_url)
        all_quotes.extend(quotes)

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(AUTHORS_FIELDS)

        for quote in all_quotes:
            writer.writerow([
                quote.text,
                quote.author,
                str(quote.tags),
            ])


if __name__ == "__main__":
    main("quotes.csv")
    print(get_quotes_from_page(URL_PAGINATION))
