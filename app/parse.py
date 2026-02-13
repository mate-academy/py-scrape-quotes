import requests
from bs4 import BeautifulSoup
import time
import csv
from dataclasses import dataclass


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def scrape_quotes() -> list[Quote]:
    quotes: list[Quote] = []
    page = 1

    session = requests.Session()

    while True:
        url = f"https://quotes.toscrape.com/page/{page}/"
        try:
            response = session.get(url, timeout=5)
        except requests.RequestException as e:
            print(f"Network error: {e}")
            break

        if response.status_code == 404:
            break

        if response.status_code == 429 or response.status_code >= 500:
            print(f"Retrying page {page} after error {response.status_code}")
            time.sleep(2)
            continue

        if response.status_code != 200:
            print(f"Unexpected status {response.status_code} on page {page}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        quote_blocks = soup.select(".quote")

        if not quote_blocks:
            break

        for block in quote_blocks:
            text = block.select_one(".text").get_text(strip=True)
            author = block.select_one(".author").get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in block.select(".tags .tag")]
            quotes.append(Quote(text=text, author=author, tags=tags))

        page += 1
        time.sleep(1)

    return quotes



def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for qts in quotes:
            writer.writerow([qts.text, qts.author, qts.tags])


if __name__ == "__main__":
    main("quotes.csv")
