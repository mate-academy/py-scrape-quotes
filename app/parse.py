import csv
import time
from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag
import requests


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com"


def get_quotes_from_page(soup: Tag) -> list[Quote]:
    quotes = []

    for quote_div in soup.find_all("div", class_="quote"):
        text = quote_div.find("span", class_="text").get_text(strip=True)
        author = quote_div.find("small", class_="author").get_text(strip=True)
        tags = [
            tag.get_text(strip=True)
            for tag in quote_div.find_all("a", class_="tag")
        ]
        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(
        output_csv_path, mode="w",
        newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


def main(output_csv_path: str) -> None:
    url = BASE_URL
    quotes: list[Quote] = []

    while True:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")

        quotes.extend(get_quotes_from_page(soup))

        next_button = soup.find("li", class_="next")
        if not next_button:
            break

        next_page = next_button.find("a")["href"]
        url = BASE_URL + next_page
        time.sleep(1)  # Be polite and avoid overwhelming the server

    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
