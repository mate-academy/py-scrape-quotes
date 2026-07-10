import csv
import time
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"
REQUEST_DELAY = 0.5


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_page_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")


def parse_quotes(soup: BeautifulSoup) -> list[Quote]:
    quotes = []

    for quote_element in soup.select(".quote"):
        text = quote_element.select_one(".text").get_text(strip=True)
        author = quote_element.select_one(".author").get_text(strip=True)

        tags = [
            tag.get_text(strip=True)
            for tag in quote_element.select(".tag")
        ]

        quotes.append(
            Quote(
                text=text,
                author=author,
                tags=tags,
            )
        )

    return quotes


def get_next_page_url(
    soup: BeautifulSoup,
    current_url: str,
) -> str | None:
    next_page_link = soup.select_one(".pager .next a")

    if next_page_link is None:
        return None

    href = next_page_link.get("href")

    if not href:
        return None

    return urljoin(current_url, href)


def write_quotes_to_csv(
    quotes: list[Quote],
    output_csv_path: str,
) -> None:
    with open(
        output_csv_path,
        "w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow(
                [
                    quote.text,
                    quote.author,
                    quote.tags,
                ]
            )


def main(output_csv_path: str) -> None:
    quotes = []
    current_url: str | None = BASE_URL

    while current_url is not None:
        soup = get_page_soup(current_url)

        page_quotes = parse_quotes(soup)
        quotes.extend(page_quotes)

        current_url = get_next_page_url(
            soup=soup,
            current_url=current_url,
        )

        if current_url is not None:
            time.sleep(REQUEST_DELAY)

    write_quotes_to_csv(
        quotes=quotes,
        output_csv_path=output_csv_path,
    )


if __name__ == "__main__":
    main("quotes.csv")
