import csv
from dataclasses import dataclass, fields
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"
HOME_URL = urljoin(BASE_URL, "/")


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_quotes_from_page(soup: BeautifulSoup) -> list[Quote]:
    return [parse_single_quote(quote) for quote in soup.select(".quote")]


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    url = BASE_URL

    while url:
        page = requests.get(url, timeout=10).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_quotes_from_page(soup))

        next_link = soup.select_one("li.next > a")
        url = urljoin(BASE_URL, next_link["href"]) if next_link else None

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
