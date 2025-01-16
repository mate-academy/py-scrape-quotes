from dataclasses import dataclass
from bs4 import BeautifulSoup
import csv
import requests
import time


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_quotes_from_page(url: str) -> list[Quote]:
    print(f"Fetching {url}...")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    quotes_elements = soup.find_all("div", class_="quote")
    quotes = []

    for element in quotes_elements:
        text = element.find("span", class_="text").get_text(strip=True)
        author = element.find("small", class_="author").get_text(strip=True)
        tags = [
            tag.get_text(strip=True)
            for tag in element.find_all("a", class_="tag")
        ]
        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def scrape_all_quotes(base_url: str) -> list[Quote]:
    quotes = []
    page_number = 1

    while True:
        url = f"{base_url}/page/{page_number}/"
        page_quotes = fetch_quotes_from_page(url)

        if not page_quotes:
            print("No more quotes found. Stopping.")
            break

        quotes.extend(page_quotes)
        print(f"Collected {len(quotes)} quotes so far...")
        page_number += 1
        time.sleep(1)

    return quotes


def save_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Text", "Author", "Tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, ", ".join(quote.tags)])


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com"
    quotes = scrape_all_quotes(base_url)
    save_quotes_to_csv(quotes, output_csv_path)
    print(
        f"Scraping completed. {len(quotes)} quotes saved to {output_csv_path}."
    )


if __name__ == "__main__":
    main("quotes.csv")
