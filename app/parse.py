import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import csv
from dataclasses import dataclass


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_quotes(base_url: str, page_num: int) -> list[Quote]:
    quotes = []

    url = urljoin(base_url, f"page/{page_num}/")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    for quote in soup.find_all("div", class_="quote"):
        text = quote.find("span", class_="text").get_text(strip=True)
        author = quote.find("small", class_="author").get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag
                in quote.find_all("a", class_="tag")]

        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def write_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([quote.__dict__ for quote in quotes])


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com/"
    quotes = []

    for page_num in range(1, 11):
        quotes.extend(get_quotes(base_url, page_num))

    write_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
