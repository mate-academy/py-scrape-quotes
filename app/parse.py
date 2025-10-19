import csv
from dataclasses import dataclass, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    tag_elems = quote.select("a.tag")
    return Quote(
        text=quote.select_one(".text").get_text(strip=True),
        author=quote.select_one(".author").get_text(strip=True),
        tags=[tag.get_text(strip=True) for tag in tag_elems],
    )


def fetch_html(url: str) -> str:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.text


def parse_page(url: str) -> list[Quote]:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    quotes: list[Quote] = []

    for unit in soup.select("div.quote"):
        quotes.append(parse_single_quote(unit))

    return quotes


def parse_all_quotes(start_url: str) -> list[Quote]:
    quotes: list[Quote] = []
    url = start_url

    while url:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        for unit in soup.select("div.quote"):
            quotes.append(parse_single_quote(unit))

        next_link = soup.select_one("li.next > a")
        if next_link:
            href = next_link.get("href")
            url = urljoin(start_url, href)
        else:
            url = None

    return quotes


def write_to_csv(csv_path: str, quotes: list[Quote]) -> None:
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = parse_all_quotes(BASE_URL)

    write_to_csv(csv_path=output_csv_path, quotes=quotes)


if __name__ == "__main__":
    main("quotes.csv")
