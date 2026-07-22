from dataclasses import dataclass
import time
import csv

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def main(output_csv_path: str) -> None:
    quotes = []
    url = BASE_URL

    while True:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for quote in soup.select(".quote"):
            quotes.append(
                Quote(
                    text=quote.select_one(".text").get_text(strip=True),
                    author=quote.select_one(".author").get_text(strip=True),
                    tags=[
                        tag.get_text(strip=True)
                        for tag in quote.select(".tag")
                    ],
                )
            )

        next_page = soup.select_one(".next a")
        if next_page is None:
            break

        time.sleep(1)
        url = BASE_URL + next_page["href"]

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow(
                [
                    quote.text,
                    quote.author,
                    ";".join(quote.tags),
                ]
            )


if __name__ == "__main__":
    main("quotes.csv")
