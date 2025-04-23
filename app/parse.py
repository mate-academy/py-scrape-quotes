from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import csv


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def fetch_page(url: str) -> tuple[str, str]:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    next_button = soup.find("li", class_="next")
    next_page_url = (
        f"https://quotes.toscrape.com{next_button.find('a')['href']}"
        if next_button
        else None
    )

    return response.text, next_page_url


def parse_quotes_from_html(html: str) -> list[Quote]:
    soup = BeautifulSoup(html, "html.parser")
    quote_divs = soup.find_all("div", class_="quote")
    quotes = []

    for div in quote_divs:
        text = div.find("span", class_="text").get_text(strip=True)
        author = div.find("small", class_="author").get_text(strip=True)
        tags = [
            tag.get_text(strip=True) for tag in div.find_all("a", class_="tag")
        ]
        quotes.append(Quote(text, author, tags))

    return quotes


def save_quotes_to_csv(quotes: list[Quote], path: str) -> None:
    with open(
        path, "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([
                quote.text,
                quote.author,
                str(quote.tags)
            ])


def main(output_csv_path: str) -> None:
    url = "https://quotes.toscrape.com/"
    all_quotes = []

    while url:
        print(f"Fetching {url}...")
        html, url = fetch_page(url)
        quotes = parse_quotes_from_html(html)
        all_quotes.extend(quotes)

    save_quotes_to_csv(all_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
