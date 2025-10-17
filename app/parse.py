import requests
from bs4 import BeautifulSoup, Tag
import csv
from dataclasses import dataclass

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def scrape_single_quote(element: Tag) -> Quote:
    text = element.select_one(".text").text
    author = element.select_one(".author").text
    tags = [tag.text for tag in element.select(".tag")]
    return Quote(
        text=text,
        author=author,
        tags=tags
    )


def scrape_quotes() -> list[Quote]:
    quotes = []
    url = BASE_URL

    while url:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup.select("div.quote"):
            quotes.append(scrape_single_quote(element))

        next_link = soup.select_one("li.next a")
        url = BASE_URL + next_link["href"] if next_link else None

    return quotes


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
