import csv
import dataclasses
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"
QUOTE_FIELDS = [f.name for f in dataclasses.fields(Quote)]


def parse_quotes() -> list[Quote]:
    quotes = []
    for page in range(1, 11):
        soup = BeautifulSoup(
            requests.get(f"{BASE_URL}page/{page}/").content, "html.parser")
        for quote in soup.select("div.quote"):
            quotes.append(Quote(
                text=quote.select_one("span.text").text,
                author=quote.select_one("small.author").text,
                tags=[tag.text for tag in quote.select("div.tags a")]
            ))
    return quotes


def write_quotes(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([dataclasses.astuple(q) for q in quotes])


def main(output_csv_path: str) -> None:
    write_quotes(parse_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
