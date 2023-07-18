import csv
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    @classmethod
    def parse_single_quote(cls, quote_html: BeautifulSoup) -> "Quote":
        return cls(
            text=quote_html.select_one(".text").text,
            author=quote_html.select_one(".author").text,
            tags=[tag.text for tag in quote_html.select(".tag")],
        )


class QuoteScraper:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    @staticmethod
    def parse_all_quotes_on_page(url: str) -> list[Quote]:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        quotes = soup.select(".quote")
        return [Quote.parse_single_quote(quote) for quote in quotes]

    def parse_quotes_from_all_pages(self) -> list[Quote]:
        all_quotes = []
        page = 1
        while True:
            url = f"{self.base_url}page/{page}/"
            parsed_quotes = self.parse_all_quotes_on_page(url)
            if not parsed_quotes:
                break
            all_quotes.extend(parsed_quotes)
            page += 1
        return all_quotes

    @staticmethod
    def write_to_csv(all_quotes: list, output_csv_path: str) -> None:
        with open(
                output_csv_path,
                mode="w",
                newline="",
                encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["text", "author", "tags"])
            for quote in all_quotes:
                writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com/"
    scraper = QuoteScraper(base_url)
    all_quotes = scraper.parse_quotes_from_all_pages()
    QuoteScraper.write_to_csv(all_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
