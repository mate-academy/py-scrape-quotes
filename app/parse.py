from abc import ABC, abstractmethod
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import csv
from typing import Iterator, List


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


class PageFetcher(ABC):
    @abstractmethod
    def fetch_pages(self, base_url: str) -> Iterator[str]:
        pass


class HttpPageFetcher(PageFetcher):
    def fetch_pages(self, base_url: str) -> Iterator[str]:
        page = 1
        while True:
            url = f"{base_url}/page/{page}"
            print(f"Fetching page {page}: {url}")
            response = requests.get(url)
            print(f"Status code: {response.status_code}")
            if not response.ok:
                print("Stopping: response not OK")
                return
            yield response.text
            page += 1


class QuoteParser(ABC):
    @abstractmethod
    def parse_quotes(self, html: str) -> List[Quote]:
        pass


class BS4QuoteParser(QuoteParser):
    def parse_quotes(self, html: str) -> List[Quote]:
        soup = BeautifulSoup(html, "html.parser")
        return [
            Quote(
                text=quote.find(
                    "span", class_="text"
                ).get_text(strip=True),
                author=quote.find(
                    "small", class_="author"
                ).get_text(strip=True),
                tags=[
                    tag.get_text(strip=True) for tag in quote.select(
                        "div.tags a.tag"
                    )
                ],
            )
            for quote in soup.find_all("div", class_="quote")
        ]


class QuoteScraper:
    def __init__(
            self, fetcher: PageFetcher,
            parser: QuoteParser,
            base_url: str
    ) -> None:
        self.fetcher = fetcher
        self.parser = parser
        self.base_url = base_url

    def scrape(self) -> List[Quote]:
        quotes = []
        for page_html in self.fetcher.fetch_pages(self.base_url):
            page_quotes = self.parser.parse_quotes(page_html)
            if not page_quotes:
                break
            quotes.extend(page_quotes)
        return quotes


def write_quotes_to_csv(quotes: List[Quote], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


def main(output_csv_path: str) -> None:
    fetcher = HttpPageFetcher()
    parser = BS4QuoteParser()
    scraper = QuoteScraper(fetcher, parser, "https://quotes.toscrape.com")
    quotes = scraper.scrape()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
