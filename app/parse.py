import csv
import time
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_quotes(html_content: bytes) -> list[str]:
    quotes = []
    soup = BeautifulSoup(html_content, "html.parser")
    quote_elements = soup.select(".quote")

    for quote_element in quote_elements:
        text = quote_element.select_one(".text").get_text(strip=True)
        author = quote_element.select_one(".author").get_text(strip=True)
        tags = [
            tag.get_text(strip=True)
            for tag in quote_element.select(".tag")
        ]
        quotes.append({"text": text, "author": author, "tags": tags})

    return quotes


def scrape_quotes_single_page(url: str) -> list[str]:
    response = requests.get(url)
    if response.status_code == 200:
        return parse_quotes(response.content)
    return []


def scrape_quotes_all_pages(output_csv_path: str) -> None:
    all_quotes = []
    page_num = 1

    while True:
        page_url = f"{BASE_URL}page/{page_num}/"
        quotes = scrape_quotes_single_page(page_url)
        if not quotes:
            break
        all_quotes.extend(quotes)
        page_num += 1
        time.sleep(1)

    write_quotes_to_csv(all_quotes, output_csv_path)


def write_quotes_to_csv(quotes: list, output_csv_path: str) -> None:
    with open(
        output_csv_path,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow(
                [quote["text"], quote["author"], quote["tags"]]
            )


def main(output_csv_path: str) -> None:
    scrape_quotes_all_pages(output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
