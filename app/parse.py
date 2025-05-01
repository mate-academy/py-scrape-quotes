import csv
from dataclasses import dataclass, fields
from urllib.parse import urljoin

import requests
from bs4 import Tag, BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [get_single_quote(quote) for quote in quotes]


def get_next_page(page_soup: BeautifulSoup) -> str | None:
    next_page = page_soup.select_one(".next a")
    if next_page:
        return next_page["href"]
    return None


def get_all_quotes() -> list[Quote]:
    text = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(text, "html.parser")

    all_quotes = get_single_page_quotes(first_page_soup)

    next_page = get_next_page(first_page_soup)
    while next_page:
        text = requests.get(urljoin(BASE_URL, next_page)).content
        page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(page_soup))
        next_page = get_next_page(page_soup)

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], filename: str) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        for quote in quotes:
            writer.writerow([
                quote.text,
                quote.author,
                ",".join(quote.tags)
            ])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_all_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
