import csv
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
QUOTE_OUTPUT_CSV_PATH = "quotes.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


class QuoteScraper:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def parse_single_quote(self, quote: BeautifulSoup) -> Quote:
        text = quote.select_one(".text").get_text()
        author = quote.select_one(".author").get_text()
        tags = quote.select(".tag")
        tags = [tag.get_text() for tag in tags]
        return Quote(text, author, tags)

    def parse_quotes_page(self) -> list[Quote]:
        page_num = 1
        page = requests.get(self.base_url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = soup.select(".quote")
        print(f"Page {page_num}")

        while soup.select_one(".next"):
            page = requests.get(
                self.base_url + soup.select_one(".next > a")["href"]
            ).content
            soup = BeautifulSoup(page, "html.parser")
            quotes.extend(soup.select(".quote"))

            if soup.select_one(".next > a"):
                page_num = (
                    int(
                        soup.select_one(".next > a")["href"].split("/")[-2]
                    ) - 1
                )
                print(f"Page {page_num}")

            # last page
            if page_num > 1 and soup.select_one(".next > a") is None:
                print(f"Page {page_num + 1}")

        return [self.parse_single_quote(quote) for quote in quotes]

    def write_quotes_to_csv(self, filename: str, quotes: list[Quote]) -> None:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file, fieldnames=["text", "author", "tags"]
            )
            writer.writeheader()

            for quote in quotes:
                quote_to_dict = asdict(quote)
                writer.writerow(quote_to_dict)

    def scrape_and_save_quotes(self, output_csv_path: str) -> None:
        quotes = self.parse_quotes_page()
        self.write_quotes_to_csv(output_csv_path, quotes)


def main(output_csv_path: str) -> None:
    scraper = QuoteScraper(BASE_URL)
    scraper.scrape_and_save_quotes(output_csv_path)


if __name__ == "__main__":
    main(QUOTE_OUTPUT_CSV_PATH)
