from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag
import requests
import csv
import time
from typing import List
from urllib.parse import urljoin
import json


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com"


def get_one_quote(quote_html: Tag) -> Quote:
    text_el = quote_html.select_one(".text")
    text = text_el.get_text(strip=True) if text_el else ""

    author_el = quote_html.select_one(".author")
    author = author_el.get_text(strip=True) if author_el else ""

    tags_container = quote_html.select_one(".tags")
    if tags_container:
        tag_elements = tags_container.find_all("a", class_="tag")
    else:
        tag_elements = []
    tags_list = [element.get_text(strip=True) for element in tag_elements]

    return Quote(text, author, tags_list)


def parse_all_pages(base_url: str) -> List[Quote]:
    all_quotes = []
    current_url = base_url

    while True:
        try:
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            quotes_on_page = soup.select(".quote")
            for quote_html in quotes_on_page:
                try:
                    all_quotes.append(get_one_quote(quote_html))
                except Exception as e:
                    print(f"Ошибка при парсинге цитаты: {e}")
                    continue

            next_page = soup.select_one(".pager .next a")
            if not next_page:
                break

            next_page_href = next_page["href"]
            current_url = urljoin(base_url, next_page_href)

            time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"Error  {current_url}: {e}")
            break

    return all_quotes


def write_quotes_to_csv(path: str, quotes: List[Quote]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])

        writer.writerows(
            [(quote.text, quote.author, str(quote.tags)) for quote in quotes]
        )


def main(output_csv_path: str) -> None:
    quotes_data = parse_all_pages(BASE_URL)
    write_quotes_to_csv(path=output_csv_path, quotes=quotes_data)


if __name__ == "__main__":
    main("quotes.csv")
