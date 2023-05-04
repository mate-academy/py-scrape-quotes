from dataclasses import dataclass
import requests
import csv
from bs4 import BeautifulSoup


url = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    text = quote.find(class_="text").get_text()
    author = quote.find(class_="author").get_text()
    tags = [tag.get_text() for tag in quote.find_all(class_="tag")]

    return Quote(text, author, tags)


def main(output_csv_path: str) -> None:
    page_num = 1
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])

        while True:
            page = requests.get(f"{url}/page/{page_num}/")
            soup = BeautifulSoup(page.content, "html.parser")
            quotes = soup.find_all(class_="quote")

            for quote in quotes:
                quote_data = parse_single_quote(quote)
                writer.writerow(
                    [
                        quote_data.text,
                        quote_data.author,
                        quote_data.tags,
                    ]
                )

            next_btn = soup.find(class_="next")
            if not next_btn:
                break
            else:
                page_num += 1


if __name__ == "__main__":
    main("quotes.csv")
