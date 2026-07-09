import csv
import time
from dataclasses import dataclass
from typing import List, Dict
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


def get_author_bio(author_url: str, cache: dict) -> str:
    if author_url in cache:
        return cache[author_url]

    try:
        response = requests.get(author_url)
        time.sleep(0.1)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            bio_description = soup.find(class_="author-description")
            if bio_description:
                bio_text = bio_description.text.strip()
                cache[author_url] = bio_text
                return bio_text
    except Exception as e:
        print(f"Error fetching bio from {author_url}: {e}")

    return ""


def parse_single_page(
    page_soup: BeautifulSoup, author_cache: dict
) -> List[Quote]:
    page_data = []
    quote_elements = page_soup.find_all(class_="quote")

    for quote_el in quote_elements:
        text = quote_el.find(class_="text").text.strip()
        author = quote_el.find(class_="author").text.strip()
        tags = [tag.text.strip() for tag in quote_el.find_all(class_="tag")]

        author_link_el = quote_el.find("a", href=True)
        if author_link_el and "author" in author_link_el["href"]:
            full_bio_url = urljoin(BASE_URL, author_link_el["href"])
            get_author_bio(full_bio_url, author_cache)

        page_data.append(Quote(text=text, author=author, tags=tags))

    return page_data


def main(output_csv_path: str) -> None:
    current_url = BASE_URL
    all_quotes_data = []
    author_cache: Dict[str, str] = {}

    print("Parsing started...")

    while current_url:
        print(f"Parsing page: {current_url}")
        try:
            response = requests.get(current_url)
            time.sleep(0.2)

            if response.status_code != 200:
                print(f"Failed to load page: {current_url}")
                break

            soup = BeautifulSoup(response.content, "html.parser")
            page_results = parse_single_page(soup, author_cache)
            all_quotes_data.extend(page_results)

            next_button = soup.find(class_="next")
            if next_button and next_button.find("a"):
                next_page_route = next_button.find("a")["href"]
                current_url = urljoin(BASE_URL, next_page_route)
            else:
                current_url = None

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    with open(
        output_csv_path, mode="w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])

        for quote in all_quotes_data:
            writer.writerow([quote.text, quote.author, str(quote.tags)])

    with open(
        "authors.csv", mode="w", newline="", encoding="utf-8"
    ) as auth_file:
        auth_writer = csv.writer(auth_file)
        auth_writer.writerow(["author_url", "biography"])
        for url, biography in author_cache.items():
            auth_writer.writerow([url, biography])

    print(f"Parsing completed! Data saved to: {output_csv_path}")


if __name__ == "__main__":
    main("quotes.csv")
