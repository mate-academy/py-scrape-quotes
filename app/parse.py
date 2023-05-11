import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
from dataclasses import dataclass

URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]
    author_bio: str = ""


def create_single_quote(quote_element: BeautifulSoup) -> Quote:
    text = quote_element.find("span", {"class": "text"}).text
    author = quote_element.find("small", {"class": "author"}).text
    tags = [tag.text for tag in quote_element.select(".tag")]
    return Quote(text=text, author=author, tags=tags)


def get_quotes(url: str) -> list:
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    quotes = []
    for quote_element in soup.select(".quote"):
        quote = create_single_quote(quote_element)
        quotes.append(quote)
    next_page = soup.select_one(".next a")
    if next_page:
        next_url = urljoin(url, next_page["href"])
        quotes.extend(get_quotes(next_url))
    return quotes


def write_quotes_to_csv(quotes: list, output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([
                quote.text,
                quote.author,
                quote.tags,
            ])


def main(output_csv_path: str) -> None:
    quotes = get_quotes(URL)
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
