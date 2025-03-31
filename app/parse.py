from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import csv
from typing import List


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_page(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_quotes(page: BeautifulSoup) -> List[Quote]:
    quotes = []
    for quote_div in page.find_all("div", class_="quote"):
        text = quote_div.find("span", class_="text").get_text()
        author = quote_div.find("small", class_="author").get_text()
        tags = [
            tag.get_text()
            for tag in quote_div.find_all("a", class_="tag")
        ]
        quotes.append(Quote(text=text, author=author, tags=tags))
    return quotes


def write_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com/page/{}/"
    page_number = 1
    all_quotes = []

    while True:
        url = base_url.format(page_number)
        page = get_page(url)
        quotes = parse_quotes(page)

        if not quotes:
            break

        all_quotes.extend(quotes)
        page_number += 1

    write_to_csv(all_quotes, output_csv_path)
    print(
        f"Scraping completed. {len(all_quotes)}"
        f" quotes saved to {output_csv_path}"
    )


if __name__ == "__main__":
    main("quotes.csv")
