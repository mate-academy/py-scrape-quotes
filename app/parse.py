import csv
import logging
import time
from dataclasses import dataclass
from urllib.parse import urljoin
from typing import Generator
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def page_generator() -> Generator[bytes, None, None]:
    current_url = BASE_URL

    while current_url:
        logging.info(f"Requesting page: {current_url}")
        try:
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()

            yield response.content

            soup = BeautifulSoup(response.content, "html.parser")
            next_button = soup.find("li", class_="next")

            if next_button and next_button.find("a"):
                relative_url = next_button.find("a")["href"]
                current_url = urljoin(current_url, relative_url)
                time.sleep(0.5)  # Be gentle to the website resources
            else:
                logging.info("All pages have been successfully processed.")
                current_url = None
        except requests.RequestException as e:
            logging.error(f"Error fetching {current_url}: {e}")
            break


def parse_page(page_content: bytes) -> list[Quote]:
    soup = BeautifulSoup(page_content, "html.parser")
    quotes_list = []

    quote_elements = soup.find_all("div", class_="quote")

    for element in quote_elements:
        text = element.find("span", class_="text").text.strip()
        author = element.find("small", class_="author").text.strip()

        tag_elements = element.find_all("a", class_="tag")
        tags = [tag.text.strip() for tag in tag_elements]

        quotes_list.append(Quote(text=text, author=author, tags=tags))

    return quotes_list


def main(output_csv_path: str) -> None:
    all_quotes: list[Quote] = []

    for page_content in page_generator():
        quotes_from_page = parse_page(page_content)
        all_quotes.extend(quotes_from_page)

    logging.info(f"Writing {len(all_quotes)} quotes to {output_csv_path}...")

    with open(output_csv_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])

        for quote in all_quotes:
            writer.writerow([quote.text, quote.author, quote.tags])

    logging.info("Done!")


if __name__ == "__main__":
    main("quotes.csv")
