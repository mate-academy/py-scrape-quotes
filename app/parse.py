import csv
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com"


def parse_single_page(url: str) -> tuple[list[Quote], str | None]:
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    quotes = []

    for quote_html in soup.select(".quote"):
        text = quote_html.find("span", class_="text").get_text()
        author = quote_html.find("small", class_="author").get_text()
        tags = [tag.get_text() for tag in quote_html.select(".tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))

    next_button = soup.select_one(".pager .next a")
    next_url = BASE_URL + next_button["href"] if next_button else None
    return quotes, next_url


def main(output_csv_path: str) -> None:
    all_quotes = []
    current_url = BASE_URL

    while current_url:
        quotes, next_url = parse_single_page(current_url)
        all_quotes.extend(quotes)
        current_url = next_url

    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])

        for quote in all_quotes:
            writer.writerow([
                quote.text,
                quote.author,
                str(quote.tags)
            ])


if __name__ == "__main__":
    main("quotes.csv")
