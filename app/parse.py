from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_quotes_from_page(soup: BeautifulSoup) -> list[Quote]:
    quotes_data = []

    quotes = soup.find_all("div", class_="quote")

    for quote in quotes:
        text = quote.find("span", class_="text").get_text(strip=True)
        author = quote.find("small", class_="author").get_text(strip=True)
        tags = [
            tag.get_text(strip=True)
            for tag in quote.find_all("a", class_="tag")
        ]
        quotes_data.append(Quote(text=text, author=author, tags=tags))

    return quotes_data


def parse_author_page(url: str) -> dict[str, str]:
    soup = get_soup(url)

    return {
        "born_date": soup.find(
            "span", class_="author-born-date"
        ).get_text(strip=True),
        "born_location": soup.find(
            "span", class_="author-born-location"
        ).get_text(strip=True),
        "description": soup.find(
            "div", class_="author-description"
        ).get_text(strip=True),
    }


def main(output_csv_path: str) -> None:
    url = BASE_URL
    all_quotes: list[Quote] = []

    while url:
        soup = get_soup(url)
        quotes = parse_quotes_from_page(soup)
        all_quotes.extend(quotes)

        next_btn = soup.find("li", class_="next")
        if next_btn:
            next_url = next_btn.find("a")["href"]
            url = urljoin(BASE_URL, next_url)
        else:
            url = None

    # запись в CSV
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])

        for quote in all_quotes:
            writer.writerow([
                quote.text,
                quote.author,
                str(quote.tags)
            ])


if __name__ == "__main__":
    main("quotes.csv")
