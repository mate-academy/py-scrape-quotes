import csv
import time
from dataclasses import dataclass
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_soup(url: str) -> BeautifulSoup | None:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        time.sleep(0.3)
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException:
        return None


def main(output_csv_path: str) -> None:
    current_page_url = BASE_URL
    all_quotes = []

    print("Начинаем парсинг цитат...")

    while current_page_url:
        soup = get_soup(current_page_url)
        if not soup:
            break

        quote_elements = soup.find_all("div", class_="quote")

        for elem in quote_elements:
            text = elem.find("span", class_="text").text.strip()
            author = elem.find("small", class_="author").text.strip()
            tags = [
                tag.text.strip() for tag in elem.find_all("a", class_="tag")
            ]

            all_quotes.append(Quote(text=text, author=author, tags=tags))

        next_button = soup.find("li", class_="next")
        if next_button:
            next_page_relative_url = next_button.find("a")["href"]
            current_page_url = urljoin(BASE_URL, next_page_relative_url)
        else:
            current_page_url = None

    with open(output_csv_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])

        for quote in all_quotes:
            writer.writerow([quote.text, quote.author, quote.tags])

    print(f"Готово! Данные сохранены в '{output_csv_path}'")


if __name__ == "__main__":
    main("quotes.csv")
