import csv
from dataclasses import dataclass, fields

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tags .tag")],
    )


def parse_page(soup: BeautifulSoup) -> list[Quote]:
    return [parse_quote(quote) for quote in soup.select(".quote")]


def get_all_quotes() -> list[Quote]:
    quotes = []
    url = BASE_URL

    with requests.Session() as session:
        while url:
            response = session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            quotes.extend(parse_page(soup))

            next_link = soup.select_one("li.next > a")
            url = BASE_URL + next_link["href"].lstrip("/") if next_link else None

    return quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
