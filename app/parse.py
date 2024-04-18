import csv
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"
CSV_PATH = "quotes.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    url = BASE_URL
    while url:
        response = requests.get(url).content
        soup = BeautifulSoup(response, "html.parser")
        quotes_div = soup.find_all("div", class_="quote")
        for quote_div in quotes_div:
            text = quote_div.find("span", class_="text").get_text(strip=True)
            author = quote_div.find(
                "small",
                class_="author"
            ).get_text(strip=True)
            tags = [
                tag.get_text(strip=True)
                for tag in quote_div.find_all("a", class_="tag")
            ]
            quote = Quote(text, author, tags)
            all_quotes.append(quote)
        next_page = soup.find("li", class_="next")
        url = BASE_URL + next_page.find("a")["href"] if next_page else None
    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            tags = str(quote.tags)
            csv_writer.writerow([quote.text, quote.author, tags])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
