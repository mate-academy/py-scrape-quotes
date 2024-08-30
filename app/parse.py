import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").get_text()
    author = quote_soup.select_one(".author").get_text()
    tags = [tag.get_text() for tag in quote_soup.select(".tags .tag")]

    return Quote(text=text, author=author, tags=tags)


def parse_page(page: BeautifulSoup) -> list[Quote]:
    quotes = page.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:
    all_quotes = []
    page_number = 1

    while True:
        response = requests.get(f"{BASE_URL}page/{page_number}/")

        if response.status_code == 404:
            break
        elif response.status_code != 200:
            print(f"Error during page load {page_number}: "
                  f"{response.status_code}")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        page_quotes = parse_page(soup)

        if not page_quotes:
            break

        all_quotes.extend(page_quotes)
        page_number += 1

    return all_quotes


def save_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    save_quotes_to_csv(quotes, output_csv_path)
    print(f"All good. Watch {output_csv_path} file")


if __name__ == "__main__":
    main("quotes.csv")
