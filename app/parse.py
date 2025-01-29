from dataclasses import dataclass
from typing import List

import requests
import csv
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def extract_quotes(soup: BeautifulSoup) -> List[Quote]:
    quotes = soup.find_all("span", attrs={"class": "text"})
    authors = soup.find_all("small", attrs={"class": "author"})
    tags = soup.find_all("div", attrs={"class": "tags"})
    return zip(quotes, authors, tags)


def write_csv(quotes_data: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=",")
        csv_writer.writerow(["text", "author", "tags"])
        for quote, author, tag in quotes_data:

            tags = tag.text.split()[1:]
            csv_writer.writerow([quote.text, author.text, tags])


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com"
    current_page = 1
    all_quotes = []

    while True:
        url = f"{base_url}/page/{current_page}"
        soup = fetch_page(url)
        parsed_quotes = extract_quotes(soup)
        all_quotes.extend(parsed_quotes)
        next_button = soup.find("li", class_="next")
        if next_button:
            current_page += 1
        else:
            break

    write_csv(all_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
