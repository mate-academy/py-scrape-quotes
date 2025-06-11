import csv
import time
from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests

BASE_URL = "http://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_quotes(soup: BeautifulSoup) -> list[Quote]:
    quotes = []
    for quote_div in soup.select(".quote"):
        text = quote_div.select_one(".text").get_text(strip=True)
        author = quote_div.select_one(".author").get_text(strip=True)
        tags = [tag.get_text(strip=True)
                for tag in quote_div.select(".tags .tag")]
        quotes.append(Quote(text, author, tags))
    return quotes


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    next_page_url = BASE_URL
    while next_page_url:
        soup = fetch_page(next_page_url)
        all_quotes.extend(parse_quotes(soup))

        next_link = soup.select_one("li.next > a")
        if next_link:
            next_page_url = BASE_URL.rstrip("/") + next_link["href"]
            time.sleep(0.5)
        else:
            break
    return all_quotes


def save_to_csv(quotes: list[Quote], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    save_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
