import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, Tag

URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.find("span", itemprop="text").text,
        author=quote.find("small").text,
        tags=[tag.text for tag in quote.find_all("a", class_="tag")],
    )


def get_quotes() -> [Quote]:
    session = requests.Session()
    next_url = URL
    all_quotes = []
    while True:
        soup = BeautifulSoup(session.get(next_url).text, "html.parser")
        quotes = soup.find_all("div", class_="quote")
        all_quotes.extend([get_single_quote(quote) for quote in quotes])
        next_page = soup.find(class_="next")
        if not next_page:
            break
        next_url = URL + next_page.find("a")["href"]
    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()

    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
