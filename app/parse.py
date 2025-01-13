from dataclasses import dataclass
import csv
import requests
from bs4 import BeautifulSoup


URL = "http://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_soup(url: str) -> BeautifulSoup:
    rsp = requests.get(url)
    rsp.raise_for_status()
    return BeautifulSoup(rsp.text, "html.parser")


def parse_quote(quote_html: BeautifulSoup) -> Quote:
    text = quote_html.find(class_="text").get_text()
    author = quote_html.find(class_="author").get_text()
    tags = [
        tag.get_text(strip=True) for tag in quote_html.find_all(class_="tag")
    ]
    return Quote(text, author, tags)


def get_page(soup: BeautifulSoup) -> list[Quote]:
    quotes_html = soup.find_all(class_="quote")
    return [parse_quote(quote_html) for quote_html in quotes_html]


def get_next_page(soup: BeautifulSoup) -> str | None:
    next_page = soup.find(class_="next")
    if next_page:
        return URL + next_page.a["href"]
    return None


def write_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, repr(quote.tags)])


def main(output_csv_path: str) -> None:
    quotes = []
    next_page = URL
    while next_page:
        soup = get_soup(next_page)
        quotes.extend(get_page(soup))
        next_page = get_next_page(soup)
    write_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
