import csv
import requests
from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin


URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.find_all("a", class_="tag")]
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> list[Quote]:
    url = URL
    all_quotes = []

    while url:
        response = requests.get(url).content
        soup = BeautifulSoup(response, "html.parser")
        quotes = get_single_page_quotes(soup)
        all_quotes.extend(quotes)
        next_page = soup.select_one(".next a")

        if next_page is None:
            break

        url = urljoin(url, next_page["href"])

    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow(
                [quote.text, quote.author, quote.tags]
            )


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
