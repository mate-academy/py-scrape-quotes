import csv
import logging
import sys
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import pandas as pd

@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s %(levelname)8s] %(message)s",
    handlers=[
        logging.FileHandler("scraping.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


def get_last_page() -> int:
    """Returns the last page number by checking when quotes end"""
    count = 1
    while True:
        try:
            content = requests.get(f"https://quotes.toscrape.com/page/{count}").content
        except requests.RequestException as e:
            logging.error(f"Failed to retrieve page {count}: {e}")
            return count - 1  # Return last successfully fetched page

        soup = BeautifulSoup(content, "html.parser")
        if not soup.select_one("div.quote"):
            logging.info(f"Last page detected: {count - 1}")
            return count - 1  # Stop if no quotes are found

        count += 1


def get_data_from_page(page: int) -> list[Quote]:
    """Scrapes all quotes from a specific page"""
    try:
        content = requests.get(f"https://quotes.toscrape.com/page/{page}").content
        soup = BeautifulSoup(content, "html.parser")
        all_quotes = soup.select("div.quote")
        quotes = [
            Quote(
                text=quote.select_one(".text").text.strip(),
                author=quote.select_one(".author").text.strip(),
                tags=[tag.text for tag in quote.select(".tag")],
            )
            for quote in all_quotes
        ]
        logging.info(f"Retrieved {len(quotes)} quotes from page {page}")
        return quotes
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve page {page}: {e}")
        return []


def main(output_csv_path: str) -> None:
    last_page = get_last_page()
    all_quotes = []

    # Loop over each page and collect quotes
    for i in range(1, last_page + 1):
        quotes = get_data_from_page(i)
        all_quotes.extend(quotes)

    # Prepare data for CSV
    data = [
        {
            "text": quote.text,
            "author": quote.author,
            "tags": quote.tags,
        }
        for quote in all_quotes
    ]
    # Write the data to CSV
    # with open(output_csv_path, "w", encoding="utf-8", newline="") as csvfile:
    #     #     fieldnames = ["text", "author", "tags"]
    #     #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     #     writer.writeheader()
    #     #     writer.writerows(data)'´
    df = pd.DataFrame(data)
    df.to_csv(output_csv_path, index=False)

    logging.info(f"Data saved to {output_csv_path}")


if __name__ == "__main__":
    main("quotes.csv")
