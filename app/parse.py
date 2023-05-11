import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
from dataclasses import dataclass


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]
    author_bio: str = ""


def get_quotes(url: str) -> list:
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    quotes = []
    for quote in soup.select(".quote"):
        text = quote.find("span", {"class": "text"}).text
        author = quote.find("small", {"class": "author"}).text
        tags = [tag.text for tag in quote.select(".tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))
    next_page = soup.select_one(".next a")
    if next_page:
        next_url = urljoin(url, next_page["href"])
        quotes.extend(get_quotes(next_url))
    return quotes


def main(output_csv_path: str) -> None:
    url = "https://quotes.toscrape.com/"
    quotes = get_quotes(url)
    for quote in quotes:
        author_url = urljoin(url, f"author/{quote.author.replace(' ', '-')}")
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([
                quote.text,
                quote.author,
                quote.tags,
            ])


if __name__ == "__main__":
    main("quotes.csv")
