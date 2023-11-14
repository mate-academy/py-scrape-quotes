import csv
from dataclasses import dataclass

from bs4 import BeautifulSoup
import requests


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


URL = "https://quotes.toscrape.com"


def create_quotes(quotes_raw: list) -> list[Quote]:
    quotes = []
    for quote in quotes_raw:
        text = quote.find("span", {"class": "text"}).text
        author = quote.find("small", {"class": "author"}).text
        tags_raw = quote.findAll("a", {"class": "tag"})
        tags = [tag.text for tag in tags_raw]
        quote = Quote(
            text=text,
            author=author,
            tags=tags,
        )
        quotes.append(quote)
    return quotes


def scrape_one_page(url: str) -> list[Quote]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    quotes_raw = soup.findAll("div", {"class": "quote"})
    return create_quotes(quotes_raw)


def check_page_exists(num_page: int) -> bool:
    response = requests.get(URL + f"/page/{num_page}/")
    soup = BeautifulSoup(response.text, "html.parser")
    return "No quotes found!" not in soup.prettify()


def scrape_all_pages() -> list[Quote]:
    all_quotes = []
    i = 1
    while check_page_exists(i):
        new_quotes = scrape_one_page(URL + f"/page/{i}/")
        all_quotes.extend(new_quotes)
        i += 1

    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


def main(output_csv_path: str) -> None:
    quotes = scrape_all_pages()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
