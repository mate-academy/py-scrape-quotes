import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import csv
from dataclasses import dataclass
from time import sleep
from typing import List


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_author_bio(author_url: str) -> str:
    author_bios = {}
    if author_url in author_bios:
        return author_bios[author_url]
    response = requests.get(author_url)
    soup = BeautifulSoup(response.text, "html.parser")
    bio = soup.find("div", class_="author-description").get_text(strip=True)
    author_bios[author_url] = bio
    return bio


def get_quote_data(quote_tag: Tag) -> Quote:
    text = quote_tag.find("span", class_="text").get_text()
    author = quote_tag.find("small", class_="author").get_text()
    tags = [tag.get_text() for tag in quote_tag.find_all("a", class_="tag")]
    return Quote(text=text, author=author, tags=tags)


def scrape_all_quotes(base_url: str) -> List[Quote]:
    page = 1
    quotes = []
    while True:
        print(f"Scraping page {page}...")
        url = f"{base_url}/page/{page}/" if page > 1 else base_url
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        quote_tags = soup.find_all("div", class_="quote")
        if not quote_tags:
            break
        for tag in quote_tags:
            quotes.append(get_quote_data(tag))
        page += 1
        sleep(1)
    return quotes


def write_to_csv(quotes: List[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            tags_string = str(quote.tags)
            writer.writerow([quote.text, quote.author, tags_string])


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com"
    quotes = scrape_all_quotes(base_url)
    write_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
