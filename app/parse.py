import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page(url):
    return requests.get(url).text


def parse_quotes():
    quotes_data = []
    page = 1

    while True:
        text = fetch_page(f"https://quotes.toscrape.com/page/{page}/")
        soup = BeautifulSoup(text, "html.parser")

        quotes = soup.find_all("div", class_="quote")
        if not quotes:
            break

        for block in quotes:
            quote = Quote(
                text=block.find("span", class_="text").get_text(),
                author=block.find("small", class_="author").get_text(),
                tags=[tag.get_text() for tag in block.find_all("a", class_="tag")],
            )
            quotes_data.append(quote)

        page += 1

    return quotes_data


def write_csv(quotes, path):
    with open(path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["TEXT", "AUTHOR", "TAG"])

        for quote in quotes:
            writer.writerow([
                quote.text,
                quote.author,
                ", ".join(quote.tags)
            ])


def main(output_csv_path: str) -> None:
    quotes = parse_quotes()
    write_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
