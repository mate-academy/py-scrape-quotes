from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag
import requests
import csv

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text.strip(),
        author=quote.select_one(".author").text.strip(),
        tags=[tag.text.strip() for tag in quote.select(".tags .tag")]
    )


def get_single_page_quote(page: Tag) -> list[Quote]:
    quotes = page.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    page_num = 1

    while True:
        url = f"{BASE_URL}/page/{page_num}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        quotes = get_single_page_quote(soup)
        if not quotes:
            break

        all_quotes.extend(quotes)

        next_button = soup.select_one(".pager .next")
        if not next_button:
            break

        page_num += 1

    return all_quotes


def save_to_csv(quotes: list[Quote], output_path: str) -> None:
    with open(output_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Text", "Author", "Tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, ", ".join(quote.tags)])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    save_to_csv(quotes, output_csv_path)
    print(f"Saved {len(quotes)} quotes in {output_csv_path}")


if __name__ == "__main__":
    main("quotes.csv")
