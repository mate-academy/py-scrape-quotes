import csv
from dataclasses import dataclass, fields, asdict
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup) -> Quote:
    text = quote_soup.select_text(".text").get_text(strip=True) if hasattr(quote_soup.select_one(".text"), "get_text") else ""
    # Для BeautifulSoup:
    text = quote_soup.select_one(".text").get_text(strip=True)
    author = quote_soup.select_one(".author").get_text(strip=True)
    tags = [tag.get_text(strip=True) for tag in quote_soup.select(".tags .tag")]
    return Quote(text=text, author=author, tags=tags)


def scrape_quotes() -> list[Quote]:
    quotes = []
    url = BASE_URL

    while url:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        quote_elements = soup.select(".quote")
        for q in quote_elements:
            quotes.append(parse_single_quote(q))

        next_btn = soup.select_one(".pager .next a")
        if next_btn:
            url = urljoin(BASE_URL, next_btn["href"])
        else:
            url = None

    return quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        for q in quotes:
            writer.writerow([q.text, q.author, ", ".join(q.tags)])


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")