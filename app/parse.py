import httpx
import csv
import logging

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dataclasses import dataclass, fields, astuple

BASE_URL = "https://quotes.toscrape.com/"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: --- %(message)s ---")


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_page(soup: BeautifulSoup) -> list[Quote]:
    quotes_tags = soup.select("div.quote")

    quotes = []
    for quote_tag in quotes_tags:
        text = quote_tag.select_one("span.text").text
        author = quote_tag.select_one("small.author").text
        tags = [tag.text for tag in quote_tag.select("a.tag")]

        quote = Quote(text=text, author=author, tags=tags)
        quotes.append(quote)

    return quotes


def get_url_next_page_or_none(soup: BeautifulSoup) -> str | None:
    a_tag = soup.select_one("li.next > a")
    return a_tag["href"] if a_tag else None


def write_scraped_quotes(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        rows = [field.name for field in fields(Quote)]
        writer.writerow(rows)

        write_generator = (astuple(quote) for quote in quotes)
        writer.writerows(write_generator)


def sync_scraper(output_csv_path: str) -> None:
    parse_url = BASE_URL

    all_quotes = []
    with httpx.Client() as client:
        while True:
            res = client.get(parse_url)
            soup = BeautifulSoup(res.text, "html.parser")

            quotes = parse_single_page(soup=soup)
            all_quotes.extend(quotes)

            next_page = get_url_next_page_or_none(soup=soup)
            if next_page:
                parse_url = urljoin(BASE_URL, next_page)
            else:
                break

    write_scraped_quotes(quotes=all_quotes, output_csv_path=output_csv_path)


def main(output_csv_path: str) -> None:
    sync_scraper(output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
