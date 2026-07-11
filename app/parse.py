import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com/"
    all_quotes = []

    page = 1

    while True:
        url = f"{base_url}/page/{page}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        quotes = soup.find_all("div", class_="quote")

        for quote in quotes:
            quote_text = quote.find("span", class_="text").get_text()
            quote_author = quote.find("small", class_="author").get_text()
            quote_tags = [tag.get_text() for tag in quote.find_all("a", class_="tag")]

            all_quotes.append(Quote(quote_text, quote_author, quote_tags))

        if not quotes:
            break
        page += 1
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["text", "author", "tags"])
        writer.writeheader()

        for quote in all_quotes:
            writer.writerow({
                "text": quote.text,
                "author": quote.author,
                "tags": quote.tags
            })




if __name__ == "__main__":
    main("quotes.csv")
