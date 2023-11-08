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
quotes = []


def create_quotes(quotes_raw: list) -> None:
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


def scrape_one_page(url: str) -> None:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    quotes_raw = soup.findAll("div", {"class": "quote"})
    create_quotes(quotes_raw)


def check_page_exists(num_page: int) -> bool:
    response = requests.get(URL + f"/page/{num_page}/")
    soup = BeautifulSoup(response.text, "html.parser")
    return "No quotes found!" not in soup.prettify()


def scrape_all_pages() -> None:
    i = 1
    while check_page_exists(i):
        scrape_one_page(URL + f"/page/{i}/")
        i += 1


def write_quotes_to_csv(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding='utf-8', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


def main(output_csv_path: str) -> None:
    scrape_all_pages()
    write_quotes_to_csv(output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")

