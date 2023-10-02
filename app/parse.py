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


def get_quotes() -> [Quote]:
    quotes = []
    page = 1

    while True:
        url = f"{BASE_URL}/page/{page}/"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            quote_divs = soup.select(".quote")

            if not quote_divs:
                break

            for quote_div in quote_divs:
                text = quote_div.select_one(".text").text
                author = quote_div.select_one(".author").text
                tags = [tag.text for tag in quote_div.select(".tag")]

                quote = Quote(text=text, author=author, tags=tags)
                quotes.append(quote)

            page += 1
        else:
            print(f"Failed to retrieve page {page}")
            break

    return quotes


def main(output_csv_path: str) -> [Quote]:
    quotes = get_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
