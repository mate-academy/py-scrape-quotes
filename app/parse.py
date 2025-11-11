from dataclasses import dataclass
import csv
import time
import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    def __post_init__(self) -> None:
        if isinstance(self.tags, str):
            cleaned = self.tags.strip()
            if cleaned.startswith("[") and cleaned.endswith("]"):
                cleaned = cleaned[1:-1]
            self.tags = [
                tag.strip().strip("'").strip('"')
                for tag in cleaned.split(",")
                if tag.strip().strip("'").strip('"')
            ]


def get_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text.strip(),
        author=quote.select_one(".author").text.strip(),
        tags=[tag.text.strip() for tag in quote.select(".tags a.tag")]
    )


def get_all_quotes() -> list[Quote]:
    quotes: list[Quote] = []
    url = BASE_URL

    while url:
        time.sleep(1)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        page_quotes = [get_single_quote(q) for q in soup.select(".quote")]
        quotes.extend(page_quotes)

        next_button = soup.select_one("li.next a")
        url = BASE_URL + next_button["href"] if next_button else None

    return quotes


def save_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, ", ".join(quote.tags)])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    save_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
