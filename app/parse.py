import requests
from bs4 import BeautifulSoup
import csv
from dataclasses import dataclass

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page(url: str) -> str:
    response = requests.get(url)
    return response.text


def parse_quotes(html: str) -> list[Quote]:
    soup = BeautifulSoup(html, "html.parser")
    quotes = []

    for quote_div in soup.find_all("div", class_="quote"):
        text = quote_div.find("span", class_="text").text
        author = quote_div.find("small", class_="author").text
        tags = [tag.text for tag in quote_div.find_all("a", class_="tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def get_next_page_url(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    next_page = soup.find("li", class_="next")
    return next_page.find("a")["href"] if next_page else None


def get_quotes_from_page(page_url: str) -> tuple[list[Quote], str]:
    html = fetch_page(page_url)
    quotes = parse_quotes(html)
    next_page_url = get_next_page_url(html)
    return quotes, next_page_url


def get_all_quotes(base_url: str) -> list[Quote]:
    current_page = "/page/1/"
    all_quotes = []

    while current_page:
        quotes, next_page_url = get_quotes_from_page(base_url + current_page)
        all_quotes.extend(quotes)
        current_page = next_page_url

    return all_quotes


def write_quote_to_csv(writer: csv.DictWriter, quote: Quote) -> None:
    writer.writerow(
        {
            "text": quote.text,
            "author": quote.author,
            "tags": str(quote.tags)
        }
    )


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for quote in quotes:
            write_quote_to_csv(writer, quote)


def main(output_csv_path: str) -> None:
    all_quotes = get_all_quotes(BASE_URL)
    write_quotes_to_csv(all_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
