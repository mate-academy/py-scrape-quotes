import csv
import time
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    def __post_init__(self) -> None:
        if isinstance(self.tags, str):
            clean = self.tags.replace("[", "").replace("]", "")
            clean = clean.replace("'", "")
            self.tags = [tag.strip() for tag in clean.split(",")]


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")


def main(output_csv_path: str) -> None:
    quotes: list[Quote] = []
    base_url = "https://quotes.toscrape.com"
    url = "/page/1/"

    while url:
        soup = get_soup(base_url + url)
        for element in soup.select(".quote"):
            text = element.select_one(".text").text
            author = element.select_one(".author").text
            tags = [tag.text for tag in element.select(".tag")]
            quotes.append(Quote(text=text, author=author, tags=tags))

        next_btn = soup.select_one(".next a")
        url = next_btn["href"] if next_btn else None
        time.sleep(0.5)

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, ", ".join(quote.tags)])


if __name__ == "__main__":
    main("quotes.csv")
