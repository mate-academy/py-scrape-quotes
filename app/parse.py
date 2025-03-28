import requests
import csv
import time
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Dict

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]




def get_quotes_from_page(url: str) -> List[Quote]:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    quotes = []
    for quote_block in soup.select(".quote"):
        text = quote_block.find(class_="text").get_text(strip=True)
        author = quote_block.find(class_="author").get_text(strip=True)
        tags = [tag.get_text(strip=True)
                for tag in quote_block.select(".tags .tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def get_all_quotes() -> List[Quote]:
    quotes = []
    page_num = 1

    while True:
        url = f"{BASE_URL}/page/{page_num}/"
        page_quotes = get_quotes_from_page(url)

        if not page_quotes:
            break

        quotes.extend(page_quotes)
        page_num += 1
        time.sleep(1)

    return quotes


def get_author_bio(author_url: str, cache: Dict[str, str]) -> str:
    if author_url in cache:
        return cache[author_url]

    response = requests.get(BASE_URL + author_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    bio = soup.select_one(".author-description").get_text(strip=True)
    cache[author_url] = bio
    return bio


def save_quotes_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


def main(output_csv_path: str) -> None:
    pass
    quotes = get_all_quotes()
    save_quotes_to_csv(quotes, output_csv_path)
    print(f"Scraped {len(quotes)} quotes and saved to {output_csv_path}")


if __name__ == "__main__":
    main("quotes.csv")
